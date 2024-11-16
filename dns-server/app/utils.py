def bytes_to_bits(byte_string: bytes):
    return "".join(format(byte, "08b") for byte in byte_string)


def bits_to_bytes(bit_string: str):
    return bytes(int(bit_string[i : i + 8], 2) for i in range(0, len(bit_string), 8))
