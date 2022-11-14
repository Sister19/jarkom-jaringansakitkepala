import lib.connection
from lib.segment import Segment
import lib.segment as segment
import socket
import lib.argparser

CLIENT_LISTEN_TIMEOUT = 4
CLIENT_LISTEN_HANDSHAKE_TIMEOUT = 10

class Client:
    def __init__(self):
        # Init client
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
        self.listen_timeout = CLIENT_LISTEN_TIMEOUT
        self.listen_shake_timeout = CLIENT_LISTEN_HANDSHAKE_TIMEOUT
        

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        
        # Create connection
        print(f"Client is listening on {self.ip}:{self.port}")
        print("[!] Initiate connection with three way handshake")
        print(f"[!] Sending broadcast SYN to port {self.server_broadcast_addr[1]}")
        req_sync = Segment()
        req_sync.set_flag([segment.SYN_FLAG])
        self.connection.send_data(req_sync, self.server_broadcast_addr)
        
        # Listen for SYN-ACK
        print("[!] Waiting for server response...")
        self.connection.set_timeout(self.listen_shake_timeout)
        try:
            res_sync = self.connection.listen_single_segment()
            res_flag = res_sync.get_flag()
            if res_flag.__FLAG:
                # Send ACK
                ack_req = Segment()
                ack_req.set_flag([segment.ACK_FLAG])
                self.connection.send_data(ack_req)
                print("[!] Connection established with server")
            else:
                print("\n[!] Invalid response : server SYN-ACK response not valid")
                print(f"[!] Exiting...")
                exit(1)
        except socket.timeout:
            print("\n[!] SYN-ACK Connection failed")
            print(f"[!] Exiting...")
            exit(1)


    def listen_file_transfer(self):
        # File transfer, client-side
        print("[!] Start transfering file...")

        self.connection.set_timeout(self.listen_timeout)
        with open(self.path, "wb") as dest:
            request_number = 0
            end_of_file = False
            while not end_of_file:
                try:
                    resp = self.connection.listen_single_segment()
                    segment_seq_number = resp.get_header()["sequence"]
                    if segment_seq_number == request_number :
                        print(f"[!] Sequence number match with Rn, sending ACK number {request_number}...")
                        dest.write(resp.get_payload())
                        if request_number >= 0:
                            ack = Segment()
                            ack.set_flag([segment.ACK_FLAG])
                            ack.set_header({"sequence":0,"ack": request_number})
                            self.connection.send_data(ack)
                        else:
                            pass
                        request_number += 1
                    elif resp.get_flag().__FLAG == segment.FIN_FLAG:
                        end_of_file = True
                        print(f"[!] FIN flag, stoping transfer...")
                        print(f"[!] Sending ACK tearing down connection...")
                        ack_resp = Segment()
                        ack_resp.set_flag([segment.ACK_FLAG])
                        self.connection.send_data(ack_resp)
                    else:
                        print(f"[!] Sequence number mismatch, ignoring...")
                
                except socket.timeout:
                    print(f"[!] Listening timeout, resending ACK {request_number-1}...")
                    request_number = request_number - 1
                    if request_number >= 0:
                        ack = Segment()
                        ack.set_flag([segment.ACK_FLAG])
                        ack.set_header({"sequence":0,"ack": request_number})
                        self.connection.send_data(ack)
                    else:
                        pass


if __name__ == '__main__':
    # test_connection
    # client = lib.connection.Connection("localhost",1234)
    # client.set_timeout(CLIENT_LISTEN_TIMEOUT)
    # msg = client.listen_single_segment()
    # print(msg)
    # client.close_socket()
    main = Client()
    main.three_way_handshake()
    # main.listen_file_transfer()
