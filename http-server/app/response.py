from dataclasses import dataclass
from app import constants


@dataclass
class Header:
    content_type: str
    content_length: int
    content_encoding: str | None = None

    def dict(self):
        base = {
            "Content-Type": self.content_type,
            "Content-Length": self.content_length,
        }
        if self.content_encoding:
            base["Content-Encoding"] = self.content_encoding
        return base

    def headers(self):
        return constants.CRLF.join(
            [f"{key}: {value}" for key, value in self.dict().items()]
        )


def response_builder(
    status: int,
    reason_phrase: str,
    header: Header | None = None,
    body: str | None = None,
    version: str = "HTTP/1.1",
):
    res = f"{version} {status} {reason_phrase}{constants.CRLF}{header.headers() if header else ''}{constants.CRLF}{constants.CRLF}"
    if body:
        res += f"{body}"
    return res


@dataclass
class Response:
    status: int
    reason_phrase: str
    header: Header | None = None
    body: str | bytes | None = None
    version: str = "HTTP/1.1"

    def build(self):
        res = f"{self.version} {self.status} {self.reason_phrase}{constants.CRLF}{self.header.headers() if self.header else ''}{constants.CRLF}{constants.CRLF}"
        if type(self.body) is str:
            res += f"{self.body}"
        if type(self.body) is bytes:
            return b"".join([res.encode(), self.body])
        return res.encode()
