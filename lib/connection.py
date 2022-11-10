import socket
from .segment import Segment
from typing import Tuple

LISTEN_BUFFER_SIZE = 2**16

class Connection:
    def __init__(self, ip : str, port : int):
        # Init UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((ip,port))

    def send_data(self, msg : Segment, dest : Tuple[str, int]):
        # Send single segment into destination
        self.sock.sendto(msg.get_bytes(), dest)

    def listen_single_segment(self) -> Segment:
        # Listen single UDP datagram within timeout and convert into segment
        data, addr = self.sock.recvfrom(LISTEN_BUFFER_SIZE)
        msg = Segment()
        msg.set_from_bytes(data)
        return msg

    def set_timeout(self, timeout: float):
        self.sock.settimeout(timeout)

    def close_socket(self):
        # Release UDP socket
        self.sock.close()
