from dataclasses import dataclass, field
from typing import Literal

@dataclass
class Header:
    pass

@dataclass
class Request:
    resource: str
    method: Literal["POST", "GET"]
    params: dict[str, str] = field(default_factory=dict)
    header: Header | None = None


