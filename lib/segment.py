import struct

# Constants 
SYN_FLAG = 0b1
ACK_FLAG = 0b1
FIN_FLAG = 0b1

class SegmentFlag:
    """
    Class untuk byte flag pada segment
    """
    def __init__(self, flag: bytes):
        # Init flag variable from flag byte

        # Input merupakan gabungan ketiga flag
        # SYN, ACK, FIN
        self.SYN = (flag >> 1) & 1
        self.ACK = (flag >> 4) & 1
        self.FIN = (flag >> 0) & 1

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        # Di-pack sebagai unsigned char
        return struct.pack("!B", self.get_flag())

    def get_flag(self) -> bytes:
        return (self.SYN << 1) + (self.ACK << 4) + (self.FIN << 0)


class Segment:
    # -- Internal Function --
    def __init__(self):
        # Initalize segment
        # pass
        self.__SEQ_NUM: int = 0
        self.__ACK_NUM: int = 0
        self.__PAYLOAD: bytes = b""
        self.__FLAG: bytes = 0b0
        self.__CHECKSUM: int = 0

    def __str__(self):
        # Optional, override this method for easier print(segmentA)
        output = ""
        output += f"{'Sequence number':24} | {self.__SEQ_NUM}\n"
        output += f"{'ACK number':24} | {self.__ACK_NUM}\n"
        output += f"{'FLAG SYN':24} | {self.__FLAG >> 1 & 0b1}\n"
        output += f"{'FLAG ACK':24} | {self.__FLAG >> 4 & 0b1}\n"
        output += f"{'FLAG FIN':24} | {self.__FLAG >> 0 & 0b1}\n"
        output += f"{'Checksum':24} | {struct.pack('@H', self.__calculate_checksum())}\n"
        output += f"{'Payload':24} | {self.__PAYLOAD}"
        return output

    def __calculate_checksum(self) -> int:
        checksum      = 0x0
        PACK_FORMAT = f"@iiBx{len(self.__PAYLOAD)}s0H"
        PACK_BYTES = struct.pack(
                PACK_FORMAT,                
                self.__SEQ_NUM,
                self.__ACK_NUM,
                self.__FLAG,
                self.__PAYLOAD
            )

        # Sum all 16-bit chunks of data
        for i in range(0, len(PACK_BYTES), 2):
            part_bytes = PACK_BYTES[i:i+2]
            [ chunk ]  = struct.unpack("H", part_bytes)
            checksum   = (checksum + chunk) & 0xFFFF

        checksum = 0xFFFF - checksum    # Unsigned 16-bit bitwise not
        return checksum


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
            self.__CHECKSUM,
            self.__PAYLOAD
        ) = struct.unpack(f"!iiBxH{PAYLOAD_SIZE}s", src)

    def get_bytes(self) -> bytes:
        # Calculate checksum
        self.__CHECKSUM = self.__calculate_checksum()
        # Convert this object to pure bytes
        PACK_FORMAT = f"!iiBxH{len(self.__PAYLOAD)}s"
        PACK_BYTES = struct.pack(
                PACK_FORMAT,                
                self.__SEQ_NUM,
                self.__ACK_NUM,
                self.__FLAG,
                self.__CHECKSUM,
                self.__PAYLOAD
            )
        return PACK_BYTES

    def get_seg(*flags) -> 'Segment':
        res_seg = Segment()

        f_syn = 0b1 if "SYN" in flags else 0b0
        f_ack = 0b1 if "ACK" in flags else 0b0
        f_fin = 0b1 if "FIN" in flags else 0b0

        res_seg.set_flag([f_syn, f_ack, f_fin])

        return res_seg

    # -- Checksum --
    def valid_checksum(self) -> bool:
        # Use __calculate_checksum() and check integrity of this object
        # print(f"{self.__calculate_checksum()} + {self.__CHECKSUM} = {self.__calculate_checksum() + self.__CHECKSUM}")
        return self.__calculate_checksum() == self.__CHECKSUM

if __name__ == "__main__":
    seg_1 = Segment.get_seg("ACK", "SYN")
    print(seg_1)
