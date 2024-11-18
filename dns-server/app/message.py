from dataclasses import dataclass, field
import struct
from typing import Literal, cast

from app import utils

import io


FOUR_BIT_INT = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
THREE_BIT_INT = Literal[0, 1, 2, 3, 4, 5, 6, 7]
ONE_BIT_INT = Literal[0, 1]


QR_REPLY_PACKET = 1
QR_QUESTION_PACKET = 0


TERMINATOR: bytes = b"\x00"


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
    def from_bytes(cls, b_msg: bytes):
        b_io = io.BytesIO(b_msg)
        id = int.from_bytes(b_io.read(2), "big")
        flags = Flags.from_bytes(b_io.read(2))
        qcount = int.from_bytes(b_io.read(2), "big")
        ancount = int.from_bytes(b_io.read(2), "big")
        nscount = int.from_bytes(b_io.read(2), "big")
        arcount = int.from_bytes(b_io.read(2), "big")
        return (
            cls(
                id=id,
                flags=flags,
                qcount=qcount,
                ancount=ancount,
                nscount=nscount,
                arcount=arcount,
            ),
            b_io.tell(),
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

    @staticmethod
    def encode_labels(labels: list["Label"]):
        return b"".join(
            [
                b"".join([label.to_bytes() for label in labels]),
                Label.terminator,
            ]
        )
    

    def to_bytes(self):
        return b"".join([self.length.to_bytes(1, "big"), self.name.encode("utf-8")])




@dataclass
class Question:
    name: str
    type: int = 1
    klass: int = 1

    @classmethod
    def from_bytes(cls, r_msg: bytes, idx: int):
        domain, idx = utils.parse_domain(r_msg,idx )
        record_type, record_class = struct.unpack("!hh", r_msg[idx : idx + 4])
        return (
            cls(
                name=domain,
                type=record_type,
                klass=record_class,
            ),
            idx + 4,
        )

    def encode(self):
        return b"".join(
            [
                utils.encode_domain(self.name),
                TERMINATOR,
                self.type.to_bytes(2, "big"),
                self.klass.to_bytes(2, "big"),
            ]
        )


@dataclass
class ResourceRecords:
    name: str
    ttl: int  # 4 bytes
    rdata: str
    rdata_parts: list[str] = field(init=False)
    rdlength: int | None = None  # 2 bytes
    type: int = 1
    klass: int = 1

    def __post_init__(self):
        ip_parts = self.rdata.split(".")
        self.rdata_parts = [part for part in ip_parts]

    def get_rdlength(self):
        if self.rdlength is None:
            self.rdlength = len(self.rdata_parts)
        return self.rdlength

    @classmethod
    def from_bytes(cls,  idx: int, r_msg: bytes):
        domain , idx = utils.parse_domain(r_msg, idx)
        rest_bio = io.BytesIO(r_msg[idx:])

        type = int.from_bytes(rest_bio.read(2), "big")
        klass = int.from_bytes(rest_bio.read(2), "big")
        ttl = int.from_bytes(rest_bio.read(4), "big")
        rdlength = int.from_bytes(rest_bio.read(2), "big")
        parts: list[int] = []
        for _ in range(rdlength):
            parts.append(int.from_bytes(rest_bio.read(1), "big"))

        rdata = ".".join([str(part) for part in parts])
        return (
            cls(
                name=domain,
                type=type,
                klass=klass,
                ttl=ttl,
                rdata=rdata,
                rdlength=rdlength,
            ),
            rest_bio.tell(),
        )

    def encode(self):
        parts = self.name.split(".")
        labels = [Label(name=part, length=len(part)) for part in parts]
        ip_bytes = b"".join([int(part).to_bytes(1, "big") for part in self.rdata_parts])
        return b"".join(
            [
                Label.encode_labels(labels),
                self.type.to_bytes(2, "big"),
                self.klass.to_bytes(2, "big"),
                self.ttl.to_bytes(4, "big"),
                self.get_rdlength().to_bytes(2, "big"),
                ip_bytes,
            ]
        )


@dataclass
class Answer:
    rrs: list[ResourceRecords]

    @classmethod
    def from_bytes(cls, idx: int, ancount: int, r_msg: bytes  ):
        count = 0
        rrs: list[ResourceRecords] = []
        while count < ancount:
            rr, idx = ResourceRecords.from_bytes(idx, r_msg)
            rrs.append(rr)
            count += 1
        return cls(rrs), idx

    def encode(self):
        return b"".join([rr.encode() for rr in self.rrs])


@dataclass
class DnsMessage:
    header: Header
    questions: list[Question]
    answer: Answer

    @classmethod
    def from_bytes(cls, b_msg: bytes):
        header, idx = Header.from_bytes(b_msg)
        questions: list[Question] = []
        for i in range(header.qcount):
            question, idx = Question.from_bytes(b_msg, idx)
            questions.append(question)



        answer, _ = Answer.from_bytes(idx, header.ancount, b_msg)
        return cls(
            header=header,
            questions=questions,
            answer=answer,
        )

    def encode(self) -> bytes:
        return b"".join(
            [
                self.header.encode(),
                b"".join([question.encode() for question in self.questions]),
                self.answer.encode(),
            ]
        )

    def __repr__(self) -> str:
        return f"""
        DNS MESSAGE
        -----------
        # Header: {self.header}
        # Questions: {self.questions}
        # Answer: {self.answer}
        """
