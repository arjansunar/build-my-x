import re
import socket
from typing import Literal, cast
from app import constants, request, response, router


app = router.Router()
app.add_route(
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
app.add_route(r"^/$", lambda request: response.response_builder(200, "OK").encode())


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
        req = request.Request(
            resource=grouped.get("resource", ""),
            method=cast(Literal["GET", "POST"], grouped.get("method", "")),  # type: ignore
        )
        res = app.run(req)
    else:
        res =response.response_builder(500, "Server Error").encode()
    conn.sendall(res)
    conn.close()


if __name__ == "__main__":
    main()
