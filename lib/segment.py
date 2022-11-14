import struct

# Constants 
SYN_FLAG = 0b0
ACK_FLAG = 0b0
FIN_FLAG = 0b0

class SegmentFlag:
    """
    Class untuk byte flag pada segment
    """
    def __init__(self, flag : bytes):
        # Init flag variable from flag byte

        # Input merupakan gabungan ketiga flag
        # SYN, ACK, FIN
        self.__FLAG = flag

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        # Di-pack sebagai unsigned char
        return struct.pack("!B", self.__FLAG)

class Segment:
    # -- Internal Function --
    def __init__(self):
        # Initalize segment
        # pass
        self.__SEQ_NUM: int = 0
        self.__ACK_NUM: int = 0
        self.__PAYLOAD: bytes = b""
        self.__FLAG: bytes = 0b0

    def __str__(self):
        # Optional, override this method for easier print(segmentA)
        output = ""
        output += f"{'Sequence number':24} | {self.__SEQ_NUM}\n"
        output += f"{'ACK number':24} | {self.__ACK_NUM}\n"
        output += f"{'FLAG SYN':24} | {self.__FLAG >> 1 & 0b1}\n"
        output += f"{'FLAG ACK':24} | {self.__FLAG >> 4 & 0b1}\n"
        output += f"{'FLAG FIN':24} | {self.__FLAG >> 0 & 0b1}\n"
        output += f"{'Checksum':24} | {self.__calculate_checksum()}\n"
        output += f"{'Payload':24} | {self.__PAYLOAD}"
        return output

    def __calculate_checksum(self) -> int:
        # Calculate checksum here, return checksum result
        return 0


    # -- Setter --
    def set_header(self, header : dict):
        self.__SEQ_NUM = header["sequence"]
        self.__ACK_NUM = header["ack"]

    def set_payload(self, payload : bytes):
        self.__PAYLOAD = payload

    def set_flag(self, flag_list : list):
        # Urutan flag harus SYN, ACK, FIN

        SYN, ACK, FIN = flag_list
        self.__FLAG = (SYN << 1) + (ACK << 4) + (FIN << 0)


    # -- Getter --
    def get_flag(self) -> SegmentFlag:
        return SegmentFlag(self.__FLAG)

    def get_header(self) -> dict:
        return {
                "sequence": self.__SEQ_NUM,
                "ack": self.__ACK_NUM
            }

    def get_payload(self) -> bytes:
        return self.__PAYLOAD

    # -- Marshalling --
    def set_from_bytes(self, src : bytes):
        # From pure bytes, unpack() and set into python variable
        PAYLOAD_SIZE = len(src) - 12 # Ukuran non-payload: 12
        (
            self.__SEQ_NUM, 
            self.__ACK_NUM,
            self.__FLAG,
            _,
            self.__PAYLOAD
        ) = struct.unpack(f"!iiBxh{PAYLOAD_SIZE}s", src)

    def get_bytes(self) -> bytes:
        # Convert this object to pure bytes
        PACK_FORMAT = f"!iiBxh{len(self.__PAYLOAD)}s"
        PACK_BYTES = struct.pack(
                PACK_FORMAT,                
                self.__SEQ_NUM,
                self.__ACK_NUM,
                self.__FLAG,
                self.__calculate_checksum(),
                self.__PAYLOAD
            )
        return PACK_BYTES

    # -- Checksum --
    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        pass

if __name__ == "__main__":
    test_segment = Segment()
    test_header = {
            "sequence": 24,
            "ack": 40
            }
    test_segment.set_header(test_header)
    test_segment.set_payload(b"Test Segment")
    test_segment.set_flag([0b0, 0b1, 0b1])
    print("Test Segment 1")
    print(test_segment)
    test_segment_2 = Segment()
    test_segment_2.set_from_bytes(test_segment.get_bytes())
    print("Test Segment 2")
    print(test_segment_2)
