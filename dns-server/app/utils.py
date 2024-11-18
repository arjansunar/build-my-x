def bytes_to_bits(byte_string: bytes):
    return "".join(format(byte, "08b") for byte in byte_string)


def bits_to_bytes(bit_string: str):
    return bytes(int(bit_string[i : i + 8], 2) for i in range(0, len(bit_string), 8))


OFFSET_MASK = 0b11_00_00_00
def is_dns_offset(bytes: bytes):
    # dns offset is 2 bytes long
    if len(bytes) < 2:
        return False

    if bytes[0] & OFFSET_MASK == OFFSET_MASK:
        return True

    return False

def extract_dns_offset(bytes: bytes):
    # turn off first two bits
    offset = bytes[0] & ~OFFSET_MASK
    # join with second byte
    offset <<= 8
    offset |= bytes[1]
    return offset
