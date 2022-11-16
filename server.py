import lib.connection
import lib.segment as segment
from lib.segment import Segment
from typing import Tuple

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

    def listen_for_clients(self):
        # Waiting client for connect
        pass

    def start_file_transfer(self):
        # Handshake & file transfer for all client
        pass

    def file_transfer(self, client_addr : Tuple[str, int]):
        # File transfer, server-side, Send file to 1 client
        pass

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
