import lib.connection
from lib.segment import Segment
import lib.segment as segment
import socket

CLIENT_LISTEN_TIMEOUT = 4
CLIENT_LISTEN_HANDSHAKE_TIMEOUT = 10

class Client:
    def __init__(self):
        # Init client
        args = {
            "port": (int, "Client port"),
            "path": (str, "Destination path")
        }
        self.ip = "localhost"
        self.server_broadcast_addr = ("",5000)
        self.path = (str, "Destination path")
        self.port = (int, "Client port")


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
        self.connection.set_timeout(CLIENT_LISTEN_HANDSHAKE_TIMEOUT)
        try:
            res_sync = self.connection.listen_single_segment()
            res_flag = res_sync.get_flag()
            if res_flag.SYN and res_flag.ACK:
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
        pass


if __name__ == '__main__':
    # test_connection
    client = lib.connection.Connection("localhost",1234)
    client.set_timeout(CLIENT_LISTEN_TIMEOUT)
    msg = client.listen_single_segment()
    print(msg)
    client.close_socket()
    # main = Client()
    # main.three_way_handshake()
    # main.listen_file_transfer()
