import lib.connection
from lib.segment import Segment
import lib.segment as segment

SERVER_TRANSFER_ACK_TIMEOUT = 1
class Server:
    def __init__(self):
        # Init server
        pass

    def listen_for_clients(self):
        # Waiting client for connect
        pass

    def start_file_transfer(self):
        # Handshake & file transfer for all client
        pass

    def file_transfer(self, client_addr : ("ip", "port")):
        # File transfer, server-side, Send file to 1 client
        pass

    def three_way_handshake(self, client_addr: ("ip", "port")) -> bool:
       # Three way handshake, server-side, 1 client
       pass


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
