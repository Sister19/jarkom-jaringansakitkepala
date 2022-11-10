import lib.connection
from lib.segment import Segment
import lib.segment as segment

CLIENT_LISTEN_TIMEOUT = 4
CLIENT_LISTEN_HANDSHAKE_TIMEOUT = 10
class Client:
    def __init__(self):
        # Init client
        pass

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        pass

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
