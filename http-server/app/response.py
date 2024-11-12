from dataclasses import dataclass
from app import constants


@dataclass
class Header:
    content_type: str
    content_length: int

    def dict(self):
        return {
            "Content-Type": self.content_type,
            "Content-Length": self.content_length,
        }

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
