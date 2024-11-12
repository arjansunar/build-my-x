from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal
from app import constants, utils

if TYPE_CHECKING:
    from main import Env


def extract_request_parts(message: str):
    parts = message.split(constants.CRLF)
    return (utils.get(parts, 0), utils.get(parts, 1))


@dataclass
class Header:
    host: str | None
    user_agent: str | None

    @classmethod
    def from_list(cls, data: list[str]):
        headers: dict[str, str] = {}
        for d in data:
            split_header_line = d.split(r": ")
            assert (
                len(split_header_line) == 2
            ), f"headers must be in <key>:<value> format got {d}"
            key, value = split_header_line
            headers[key] = value
        return cls(
            host=headers.get("Host"), user_agent=headers.get("User-Agent")
        )


@dataclass
class Request:
    resource: str
    method: Literal["POST", "GET"]
    env: "Env"
    params: dict[str, str] = field(default_factory=dict)
    header: Header | None = None
