import re
import socket
from dataclasses import dataclass
from typing import Callable, Literal, cast

CRLF = "\r\n"

REQUEST_MATCHER = r"(?P<method>GET|POST) (?P<resource>/[\w./]*)"
PATH_PARAM_MATCHER = r"\{(?P<path_param>\w+)\}"


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
        return CRLF.join([f"{key}: {value}" for key, value in self.dict().items()])


def response_builder(
    status: int,
    reason_phrase: str,
    header: Header | None = None,
    body: str | None = None,
    version: str = "HTTP/1.1",
):
    res = f"{version} {status} {reason_phrase}{CRLF}{header.headers() if header else ''}{CRLF}{CRLF}"
    if body:
        res += f"{body}"
    return res


@dataclass
class Request:
    resource: str
    method: Literal["POST", "GET"]
    remaining_path: str | None = None
    params: dict[str, str] = {}


class Router:
    route_map: dict[str, Callable[[Request], bytes]] = {}

    def add_route(self, path: str, handler: Callable[[Request], bytes]):
        self.route_map[path] = handler

    def run(self, request: Request) -> bytes:
        for path, handler in self.route_map.items():
            path_param_match = re.findall(PATH_PARAM_MATCHER, path)
            has_path_param = bool(path_param_match)
            if has_path_param:
                for key in path_param_match:
                    # TODO: find value for given key
                    request.params[key] = "value"

            if request.resource.startswith(path):
                remaining_path = request.resource[len(path) :]
                if remaining_path:
                    request.remaining_path = remaining_path
                return handler(request)
        # none path matched
        return response_builder(404, "Not Found").encode()


router = Router()
router.add_route(
    "/echo/{payload}",
    lambda request: response_builder(
        200,
        "OK",
        header=Header(
            content_type="text/plain",
            content_length=len(request.remaining_path) if request.remaining_path else 0,
        ),
        body=request.remaining_path,
    ).encode(),
)
router.add_route("/", lambda request: response_builder(200, "OK").encode())


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, _ = server_socket.accept()  # wait for client
    handle_connection(conn)

def handle_connection(conn: socket.socket):
    message = conn.recv(1024).decode()
    request = message.split(CRLF)
    match = re.search(REQUEST_MATCHER, request[0])
    if match:
        grouped = match.groupdict()
        request = Request(
            resource=grouped.get("resource", ""),
            method=cast(Literal["GET", "POST"], grouped.get("method", "")),  # type: ignore
        )
        response = router.run(request)
    else:
        response = response_builder(500, "Server Error").encode()
    conn.sendall(response)
    conn.close()


if __name__ == "__main__":
    main()
