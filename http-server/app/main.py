import re
import socket
from dataclasses import dataclass, field
from typing import Callable, Literal, cast
from app import constants, request, response



@dataclass
class Request:
    resource: str
    method: Literal["POST", "GET"]
    params: dict[str, str] = field(default_factory=dict)
    header: request.Header | None = None


class Router:
    route_map: dict[str, Callable[[Request], bytes]] = {}

    def add_route(self, path: str, handler: Callable[[Request], bytes]):
        self.route_map[path] = handler

    def run(self, request: Request) -> bytes:
        for path, handler in self.route_map.items():
            match = re.search(path, request.resource)
            if match:
                request.params = match.groupdict()
                return handler(request)
        # none path matched
        return response.response_builder(404, "Not Found").encode()


router = Router()
router.add_route(
    path=r"^/echo/(?P<path_param>\w+)$",
    handler=lambda request: response.response_builder(
        200,
        "OK",
        header=response.Header(
            content_type="text/plain",
            content_length=len(request.params.get("path_param", "")),
        ),
        body=request.params.get("path_param", ""),
    ).encode(),
)
router.add_route(r"^/$", lambda request: response.response_builder(200, "OK").encode())


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, _ = server_socket.accept()  # wait for client
    handle_connection(conn)


def handle_connection(conn: socket.socket):
    message = conn.recv(1024).decode()
    req = message.split(constants.CRLF)
    match = re.search(constants.REQUEST_MATCHER, req[0])
    if match:
        grouped = match.groupdict()
        req = Request(
            resource=grouped.get("resource", ""),
            method=cast(Literal["GET", "POST"], grouped.get("method", "")),  # type: ignore
        )
        res = router.run(req)
    else:
        res =response.response_builder(500, "Server Error").encode()
    conn.sendall(res)
    conn.close()


if __name__ == "__main__":
    main()
