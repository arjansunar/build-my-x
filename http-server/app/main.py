import re
import socket
import threading
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


app.add_route(
    r"^/user-agent$",
    lambda request: response.response_builder(
        200,
        "OK",
        body=request.header.user_agent if request.header else None,
        header=response.Header(
            content_type="text/plain",
            content_length=len(request.header.user_agent or "" if request.header else ""),
        ),
    ).encode(),
)
app.add_route(r"^/$", lambda request: response.response_builder(200, "OK").encode())


def main():
    host = "localhost"
    port = 4221
    server_socket = socket.create_server((host, port), reuse_port=True)
    print(f"Server listening on {host}:{port}...")
    try:
        while True: 
            conn, _ = server_socket.accept()  # wait for client
            client_thread = threading.Thread(target=handle_connection, args=(conn,))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server")


def handle_connection(conn: socket.socket):
    message = conn.recv(1024).decode()
    message_parts = message.split(constants.CRLF * 2)
    assert len(message_parts) > 0
    msg_req = message_parts[0].split(constants.CRLF)
    # msg_body =utils.get(message_parts, 1)  # noqa: F841
    request_line = msg_req[0]
    match = re.search(constants.REQUEST_LINE_MATCHER, request_line)
    if match:
        grouped = match.groupdict()
        headers_line = msg_req[1:]
        req = request.Request(
            resource=grouped.get("resource", ""),
            method=cast(Literal["GET", "POST"], grouped.get("method", "")),  # type: ignore
            header=request.Header.from_list(headers_line),
        )
        res = app.run(req)
    else:
        res = response.response_builder(500, "Server Error").encode()
    conn.sendall(res)
    conn.close()


if __name__ == "__main__":
    main()
