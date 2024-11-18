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


def parse_domain(buf: bytes, i: int = 0) -> tuple[str, int]:
    parts: list[str] = []
    while True:
        if buf[i] & OFFSET_MASK:
            offset = ((buf[i] & ~OFFSET_MASK) << 8) + buf[i + 1]
            domain, _ = parse_domain(buf, offset)
            parts.append(domain)
            return ".".join(parts), i + 2

        name_len = buf[i]
        i += 1
        if name_len == 0:
            break
        name = buf[i : i + name_len].decode()
        i += name_len
        parts.append(name)
    return ".".join(parts), i


def encode_domain(domain: str) -> bytes:
    parts = domain.split(".")
    return b"".join(
        [
            b"".join([len(part).to_bytes(1, "big"), part.encode("utf-8")])
            for part in parts
        ]
    )
