import lib.connection
import lib.segment as segment
from lib.segment import Segment
from typing import Tuple
import math
import socket

SERVER_TRANSFER_ACK_TIMEOUT = 1
class Server:
    def __init__(self):
        # Init server
        args = {
            "port": (int, "Client port"),
            "path": (str, "Destination path")
            # "-s": (None, "Show information of segment"),
            # "-p": (None, "Show payload of a segment in hexadecimal")
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
        self.total_segment = math.ceil(self.filesize/32768)
        self.window_size = 10
        self.connection.set_listen_timeout(SERVER_TRANSFER_ACK_TIMEOUT)

    def listen_for_clients(self):
        # Waiting client for connect
        # pass
        self.__client_connected = False
        self.__client_addr = 0

        while not self.__client_connected:
            try:
                data: Segment, addr: Tuple[str, int] = self.connection.listen_single_segment()
                if (data.valid_checksum() and data.get_flag().SYN):
                    self.client_conn_list.append(addr)
                    print(f"[!] Client ({addr[0]}:{addr[1]}) found")
                    self.__client_connected = True
                    self.__client_addr = addr
            except socket.timeout:
                self.__client_connected = False
                self.__client_addr = 0

    def start_file_transfer(self):
        # Handshake & file transfer for all client
        pass

    def file_transfer(self, client_addr : Tuple[str, int]):
        # File transfer, server-side, Send file to 1 client
        seq_base = 0
        N = 10
        seq_max = math.min(seq_base + N, self.total_segment)

        with open(self.path, "rb") as src:
            while seq_base < self.total_segment:
                # send next segment or resend from min segment that haven't been acked
                for seq_num in range(seq_base, seq_max):
                    data_segment = Segment()
                    src.seek(32768*seq_num)
                    data_segment.set_payload(src.read(32768))
                    data_segment.set_header({"sequence": seq_num, "ack": 0})
                    self.conn.send_data(data_segment, client_addr)
                    print(f"[!] Sending segment {seq_num} to client {client_addr[0]}:{client_addr[1]}") 
                last_seq_sent = seq_max-1
                # listen until all ack or timeout
                while seq_base <= last_seq_sent:
                    try:
                        ack_segment, addr = self.conn.listen_single_segment()
                        # checksum_valid = ack_segment.checksum_valid()
                        if (addr == client_addr and ack_segment.get_flag().get_flag_bytes()&segment.ACK_FLAG):
                            ack_num = ack_segment.get_header()["ack"]
                            if(ack_num == seq_base):
                                seq_base += 1
                                seq_max = math.min(seq_base + N, self.total_segment)
                                print(f"[!] ACK {ack_num} received from client {client_addr[0]}:{client_addr[1]}, next sequence base = {seq_base}")
                            elif ack_num > seq_base:
                                seq_base = ack_num+1
                                seq_max = math.min(seq_base + N, self.total_segment)
                                print(f"[!] ACK {ack_num} received from client {client_addr[0]}:{client_addr[1]}, shifting sequence base to {seq_base}")
                            else:
                                print(f"[!] ACK {ack_num} less than {seq_base} received from client {client_addr[0]}:{client_addr[1]}, Ignoring...")
                        elif addr!=client_addr:
                            print(f"[!] Ignoring segment: from different client...")
                        else:
                            print(f"[!] Ignoring segment: not ACK")
                    except socket.timeout:
                        print(f"[!] Segment {seq_base} not acknowledged by client {client_addr[0]}:{client_addr[1]}")
                        break
        
            print(f"[!] File transfer completed for client {client_addr[0]}:{client_addr[1]}")
            print("[!] Closing connection, sending FIN to client")
            fin_segment = Segment()
            fin_segment.set_flag(segment.FIN_FLAG)
            self.conn.send_data(fin_segment, client_addr)

            try:
                finack_segment, addr = self.conn.listen_single_segment()
                if (addr == client_addr and finack_segment.get_flag()&segment.ACK_FLAG):
                    print(f"[!] FIN-ACK received from client {client_addr[0]}:{client_addr[1]}")
                    print("[!] Closing connection, sending ACK to client")
                    ack_segment = Segment()
                    ack_segment.set_flag(segment.ACK_FLAG)
                    self.conn.send_data(ack_segment, client_addr)
            except socket.timeout:
                print(f"[!] FIN-ACK not received from client {client_addr[0]}:{client_addr[1]}, force closing connection")
        

    def three_way_handshake(self, client_addr : Tuple[str, int]) -> bool:
        # Three way handshake, server-side, 1 client
        resp_synack = Segment()
        resp_synack.set_flag([segment.SYN_FLAG, segment.ACK_FLAG])
        self.connection.send_data(resp_synack, client_addr)

        # Listen for ACK
        msg, addr = self.connection.listen_single_segment()
        ack_flag = msg.get_flag()
        if ack_flag.__FLAG == segment.ACK_FLAG:
            print(f"[!] Connection established with client {client_addr[0]}:{client_addr[1]}")
            return True
        else:
            print(f"[!] Invalid response : client ACK response not valid")
            print(f"[!] Handshake failed with client {client_addr[0]}:{client_addr[1]}")
            return False

if __name__ == '__main__':
    server = lib.connection.Connection("localhost",1337)
    test_segment = Segment()
    test_header = {
            "sequence": 24,
            "ack": 40
            }
    test_segment.set_header(test_header)
    test_segment.set_payload(b"Test Segment")
    test_segment.set_flag([0b0, 0b1, 0b1])    
    server.set_timeout(SERVER_TRANSFER_ACK_TIMEOUT)
    server.send_data(test_segment,("localhost",1234))
    server.close_socket()
    # main = Server()
    # main.listen_for_clients()
    # main.start_file_transfer()

