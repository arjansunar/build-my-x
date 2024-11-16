from dataclasses import dataclass
from typing import Literal, cast

from app import utils

import io


FOUR_BIT_INT = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
THREE_BIT_INT = Literal[0, 1, 2, 3, 4, 5, 6, 7]
ONE_BIT_INT = Literal[0, 1]


QR_REPLY_PACKET = 1
QR_QUESTION_PACKET = 0


@dataclass()
class Flags:
    qr: ONE_BIT_INT
    opcode: FOUR_BIT_INT
    aa: ONE_BIT_INT
    tc: ONE_BIT_INT
    rd: ONE_BIT_INT
    ra: ONE_BIT_INT
    z: THREE_BIT_INT
    rcode: FOUR_BIT_INT

    @classmethod
    def from_bytes(cls, b_flag: bytes) -> "Flags":
        bits = utils.bytes_to_bits(b_flag)
        return cls(
            qr=cast(ONE_BIT_INT, int(bits[0])),
            opcode=cast(FOUR_BIT_INT, int(bits[1:5], 2)),
            aa=cast(ONE_BIT_INT, int(bits[5])),
            tc=cast(ONE_BIT_INT, int(bits[6])),
            rd=cast(ONE_BIT_INT, int(bits[7])),
            ra=cast(ONE_BIT_INT, int(bits[8])),
            z=cast(THREE_BIT_INT, int(bits[9:12], 2)),
            rcode=cast(FOUR_BIT_INT, int(bits[12:16], 2)),
        )

    def encode(self):
        # Construct the 16-bit flags field based on the individual components
        # Uses big endian format (bits are placed in reverse order)
        return (
            (self.qr << 15)
            | (self.opcode << 11)  # opcode is 4 bits 11 till 14th position
            | (self.aa << 10)
            | (self.tc << 9)
            | (self.rd << 8)
            | (self.ra << 7)
            | (self.z << 4)
            | self.rcode
        ).to_bytes(2, "big")


@dataclass
class Header:
    id: int
    flags: Flags
    qcount: int
    ancount: int
    nscount: int
    arcount: int

    @classmethod
    def from_bytes(cls, b_msg: bytes) -> "Header":
        b_io = io.BytesIO(b_msg)
        id = int.from_bytes(b_io.read(2), "big")
        flags = Flags.from_bytes(b_io.read(2))
        qcount = int.from_bytes(b_io.read(2), "big")
        ancount = int.from_bytes(b_io.read(2), "big")
        nscount = int.from_bytes(b_io.read(2), "big")
        arcount = int.from_bytes(b_io.read(2), "big")
        return cls(
            id=id,
            flags=flags,
            qcount=qcount,
            ancount=ancount,
            nscount=nscount,
            arcount=arcount,
        )

    def encode(self) -> bytes:
        return b"".join(
            [
                self.id.to_bytes(2, "big"),
                self.flags.encode(),
                self.qcount.to_bytes(2, "big"),
                self.ancount.to_bytes(2, "big"),
                self.nscount.to_bytes(2, "big"),
                self.arcount.to_bytes(2, "big"),
            ]
        )


@dataclass
class Label:
    name: str
    length: int

    terminator: bytes = b"\x00"
    # @classmethod
    # def from_bytes(cls, b_msg: bytes):
    #     bio = io.BytesIO(b_msg)
    #     return cls(
    #         name=bio.read(1),
    #         length=int.from_bytes(bio.read(), "big"),
    #     )

    def to_bytes(self):
        return b"".join([self.length.to_bytes(1, "big"), self.name.encode("utf-8")])


@dataclass
class Question:
    name: str
    type: int = 1
    klass: int = 1

    # @classmethod
    # def from_bytes(cls, b_msg: bytes):
    #     return cls(
    #         name= b_msg[:2],
    #         type=int.from_bytes(b_msg[2:4], "big"),
    #         klass=int.from_bytes(b_msg[4:6], "big"),
    #     )
    def encode(self):
        parts = self.name.split(".")
        labels = [Label(name=part, length=len(part)) for part in parts]
        return b"".join(
            [
                b"".join([label.to_bytes() for label in labels]),
                Label.terminator,
                self.type.to_bytes(2, "big"),
                self.klass.to_bytes(2, "big"),
            ]
        )


@dataclass
class DnsMessage:
    header: Header
    question: Question

    @classmethod
    def from_bytes(cls, b_msg: bytes):
        b_io = io.BytesIO(b_msg)
        b_header = b_io.read(12)
        return cls(
            header=Header.from_bytes(b_header),
            # TODO: implement this
            question=Question(
                name="testing",
            ),
        )

    def encode(self) -> bytes:
        return b"".join([self.header.encode(), self.question.encode()])
