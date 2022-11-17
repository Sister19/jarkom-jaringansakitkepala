import lib.connection
import lib.argparser
import lib.segment as segment
from lib.segment import Segment
from typing import Tuple
import math
import socket

SERVER_TRANSFER_ACK_TIMEOUT = 0.5

class Server:
    def __init__(self):
        # Init server
        args = {
            "port": (int, "Client port"),
            "path": (str, "Destination path")
        }
        parser = lib.argparser.ArgumentParser("Client", args)
        args = parser.parse_args()
        
        self.ip = "localhost"
        self.port = args.port
        self.path = args.path
        self.connection = lib.connection.Connection(self.ip, self.port)
        self.server_broadcast_addr = ("",5000)
        with open(self.path, "rb") as src:
            src.seek(0,2)
            self.file_size = src.tell()
        self.total_segment = math.ceil(self.file_size/32756)
        self.window_size = 10
        self.connection.set_timeout(SERVER_TRANSFER_ACK_TIMEOUT)
        self.__client_list = [] # Isinya addr

    def listen_for_clients(self):
        # Waiting client for connect
        # pass
        new_client = True
        while new_client:
            try:
                print(f"[!] Listening for clients...")
                data, addr, isValidChecksum = self.connection.listen_single_segment()
                if (
                    isValidChecksum 
                    and data.get_flag().SYN 
                    and addr not in self.__client_list
                    ):

                    print(f"[!] New client found at {addr[0]}:{addr[1]}")
                    self.__client_list.append(addr)

                elif addr in self.__client_list:
                    print(f"[!] Existing client at {addr[0]}:{addr[1]} found, ignored")

                ask_new_client = input("[?] Listen more? (y/N) ")
                new_client = ask_new_client.lower() == 'y'

            except socket.timeout:
                print(f"[!] Socket timeout")

    def start_file_transfer(self):
        # Start file transfer
        print("[!] Initiating three way handshake with client...")
        disconn_client = []
        for conn_client in self.__client_list:
            print(f"[!] Sending SYN-ACK to client at {conn_client[0]}:{conn_client[1]}")
            is_success = self.three_way_handshake(conn_client)
            if not is_success:
                print(f"[!] Three way handshake with client at {conn_client[0]}:{conn_client[1]} failed, removing client")
                disconn_client.append(conn_client)
        for conn_client in disconn_client:
            self.__client_list.remove(conn_client)
        for conn_client in self.__client_list:
            print(f"[!] Starting file transfer to client at {conn_client[0]}:{conn_client[1]}")
            self.file_transfer(conn_client)

    def file_transfer(self, client_addr : Tuple[str, int]):
        seq_base = 0
        N = 5
        seq_max = min(seq_base + N, self.total_segment)

        with open(self.path, "rb") as src:
            while seq_base < self.total_segment:
                # send next segment or resend from min segment that haven't been acked
                for seq_num in range(seq_base, seq_max):
                    data_segment = Segment()
                    src.seek(32756*seq_num)
                    data_segment.set_payload(src.read(32756))
                    data_segment.set_header({"sequence": seq_num, "ack": 0})
                    self.connection.send_data(data_segment, client_addr)
                    print(f"[!] Sending segment {seq_num} to client at {client_addr[0]}:{client_addr[1]}") 
                last_seq_sent = seq_max-1
                # listen until all ack or timeout
                while seq_base <= last_seq_sent:
                    try:
                        ack_segment, addr, isValidChecksum = self.connection.listen_single_segment()
                        if (addr == client_addr and isValidChecksum and ack_segment.get_flag().ACK):
                            ack_num = ack_segment.get_header()["ack"]
                            if(ack_num == seq_base):
                                seq_base += 1
                                seq_max = min(seq_base + N, self.total_segment)
                                print(f"[!] ACK {ack_num} received from client at {client_addr[0]}:{client_addr[1]}, next sequence base = {seq_base}")
                            elif ack_num > seq_base:
                                seq_base = ack_num+1
                                seq_max = min(seq_base + N, self.total_segment)
                                print(f"[!] ACK {ack_num} received from client at {client_addr[0]}:{client_addr[1]}, shifting sequence base to {seq_base}")
                            else:
                                print(f"[!] ACK {ack_num} less than {seq_base} received from client at {client_addr[0]}:{client_addr[1]}, Ignoring...")
                        elif addr!=client_addr:
                            print(f"[!] Ignoring segment: from different client...")
                        elif not isValidChecksum:
                            print(f"[!] Dropping segment: invalid checksum...")
                        else:
                            print(f"[!] Ignoring segment: not ACK")
                    except socket.timeout:
                        print(f"[!] Segment {seq_base} not acknowledged by client at {client_addr[0]}:{client_addr[1]}")
                        break
        
            print(f"[!] File transfer completed for client at {client_addr[0]}:{client_addr[1]}")
            print("[!] Closing connection, sending FIN to client")

            fin_ack_received = False
            try:
                # resend fin until response = fin-ack or no response
                while not fin_ack_received:
                    fin_segment = Segment.get_seg("FIN")
                    self.connection.send_data(fin_segment, client_addr)
                    finack_segment, addr, isValidChecksum = self.connection.listen_single_segment()
                    if (addr == client_addr and isValidChecksum and finack_segment.get_flag().FIN and finack_segment.get_flag().ACK):
                        fin_ack_received = True
                        print(f"[!] FIN-ACK received from client at {client_addr[0]}:{client_addr[1]}")
                        print("[!] Closing connection, sending ACK to client")
                        ack_segment = Segment.get_seg("ACK")
                        self.connection.send_data(ack_segment, client_addr)
            except socket.timeout:
                # no response and fin-ack not received
                if not fin_ack_received:
                    print(f"[!] FIN-ACK not received from client at {client_addr[0]}:{client_addr[1]}, force closing connection")
        

    def three_way_handshake(self, client_addr : Tuple[str, int]) -> bool:

        resp_synack = Segment.get_seg("SYN", "ACK")
        self.connection.send_data(resp_synack, client_addr)

        # Listen for ACK
        try:
            msg, addr, isValidChecksum = self.connection.listen_single_segment()
            ack_flag = msg.get_flag()
            if ack_flag.ACK == segment.ACK_FLAG and isValidChecksum:
                print(f"[!] Connection established with client at {client_addr[0]}:{client_addr[1]}")
                return True
            else:
                print(f"[!] Invalid response : client ACK response not valid")
                print(f"[!] Handshake failed with client at {client_addr[0]}:{client_addr[1]}")
                return False
        except socket.timeout:
                print("[!] Handshake Ack response timeout...")
                print(f"[!] Handshake failed with client at {client_addr[0]}:{client_addr[1]}")    

if __name__ == '__main__':
    main = Server()
    main.listen_for_clients()
    main.start_file_transfer()

