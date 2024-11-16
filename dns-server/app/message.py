from dataclasses import dataclass, field
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
            b_io.read(),
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
    def parse(b_msg: bytes | io.BytesIO):
        if isinstance(b_msg, io.BytesIO):
            bio = b_msg
        else:
            bio = io.BytesIO(b_msg)
        length = int.from_bytes(bio.read(1), "big")
        return (
            bio.read(length).decode(),
            length,
            bio,
        )

    @classmethod
    def from_bytes(cls, b_msg: bytes | io.BytesIO):
        name, length, left = cls.parse(b_msg)
        return cls(name, length), left

    @staticmethod
    def encode_labels(labels: list["Label"]):
        return b"".join(
            [
                b"".join([label.to_bytes() for label in labels]),
                Label.terminator,
            ]
        )

    @staticmethod
    def extract_label_sequence(b_msg: bytes):
        """
        Extracts out the label sequence and returns remaining bytes from the message
        """
        terminator_idx = b_msg.find(Label.terminator)
        b_labels = b_msg[:terminator_idx]
        remaining = b_msg[terminator_idx + 1 :]
        b_label_size = len(b_labels)

        labels: list[Label] = []
        current_bytes: bytes | io.BytesIO = b_labels
        while True:
            label, left = Label.from_bytes(current_bytes)
            labels.append(label)
            if left.tell() == b_label_size:
                break
            current_bytes = left

        return labels, remaining

    def to_bytes(self):
        return b"".join([self.length.to_bytes(1, "big"), self.name.encode("utf-8")])


@dataclass
class Question:
    name: str
    type: int = 1
    klass: int = 1

    @classmethod
    def from_bytes(cls, b_msg: bytes):
        labels, rest = Label.extract_label_sequence(b_msg)
        rest_bio = io.BytesIO(rest)
        return (
            cls(
                name=".".join([label.name for label in labels]),
                klass=int.from_bytes(rest_bio.read(2), "big"),
                type=int.from_bytes(rest_bio.read(2), "big"),
            ),
            rest_bio.read(),
        )

    def encode(self):
        parts = self.name.split(".")
        labels = [Label(name=part, length=len(part)) for part in parts]
        return b"".join(
            [
                Label.encode_labels(labels),
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
    def from_bytes(cls, b_msg: bytes):
        labels, rest = Label.extract_label_sequence(b_msg)
        rest_bio = io.BytesIO(rest)

        type = int.from_bytes(rest_bio.read(2), "big")
        klass = int.from_bytes(rest_bio.read(2), "big")
        ttl = int.from_bytes(rest_bio.read(4), "big")
        rdlength = int.from_bytes(rest_bio.read(2), "big")
        rdata = rest_bio.read(rdlength).decode()
        return (
            cls(
                name=".".join([label.name for label in labels]),
                type=type,
                klass=klass,
                ttl=ttl,
                rdata=rdata,
                rdlength=rdlength,
            ),
            rest_bio.read(),
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
    def from_bytes(cls, b_msg: bytes, ancount: int):
        count = 0
        rrs: list[ResourceRecords] = []
        while count < ancount:
            rr, b_msg = ResourceRecords.from_bytes(b_msg)
            rrs.append(rr)
            count += 1
        return cls(rrs), b_msg

    def encode(self):
        return b"".join([rr.encode() for rr in self.rrs])


@dataclass
class DnsMessage:
    header: Header
    question: Question
    answer: Answer

    @classmethod
    def from_bytes(cls, b_msg: bytes):
        header, rest = Header.from_bytes(b_msg)
        question, rest = Question.from_bytes(rest)
        answer, rest = Answer.from_bytes(rest, header.ancount)
        return cls(
            header=header,
            question=question,
            answer=answer,
        )

    def encode(self) -> bytes:
        return b"".join(
            [self.header.encode(), self.question.encode(), self.answer.encode()]
        )
