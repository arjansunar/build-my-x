import argparse
from dataclasses import dataclass
import re
import socket
import threading
from typing import Literal, cast
from app import constants, request, response, router, utils


app = router.Router()


@app.get(path=r"^/echo/(?P<path_param>\w+)$")
def echo(request: request.Request):
    return response.Response(
        200,
        "OK",
        header=response.Header(
            content_type="text/plain",
            content_length=len(request.params.get("path_param", "")),
        ),
        body=request.params.get("path_param", ""),
    )


@app.get(r"^/user-agent$")
def user_agent_echo(request: request.Request):
    return response.Response(
        200,
        "OK",
        body=request.header.user_agent if request.header else None,
        header=response.Header(
            content_type="text/plain",
            content_length=len(
                request.header.user_agent or "" if request.header else ""
            ),
        ),
    )


@app.get(r"^/files/(?P<path_param>[\w./]+)$")
def get_file(request: request.Request):
    file_path = request.params.get("path_param")

    if file_path is None:
        return response.Response(404, "Not Found")
    file_path = f"{request.env.directory}/{file_path}"
    file = utils.get_file_at_path(file_path)
    if file is None:
        return response.Response(404, "Not Found")
    return response.Response(
        200,
        "OK",
        header=response.Header(constants.ContentType.octet_stream, len(file)),
        body=file.decode(),
    )


@app.get(r"^/$")
def index(request: request.Request):
    return response.Response(200, "OK")


@app.post(r"/files/(?P<filename>[\w./]+)$")
def create_file(request: request.Request):
    filename = request.params.get("filename")
    if request.body is None or filename is None:
        return response.Response(400, "Bad Request")
    file_path = f"{request.env.directory}/{filename}"
    utils.create_file_at_path(file_path, request.body)
    return response.Response(201, "Created")


@dataclass
class Env:
    directory: str | None


def main():
    directory = get_directory_arg()

    host = "localhost"
    port = 4221
    server_socket = socket.create_server((host, port), reuse_port=True)
    print(f"Server listening on {host}:{port}...")
    try:
        while True:
            conn, _ = server_socket.accept()  # wait for client
            client_thread = threading.Thread(
                target=handle_connection, args=(conn, Env(directory=directory))
            )
            client_thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server")


def handle_connection(conn: socket.socket, env: Env):
    message = conn.recv(1024).decode()
    message_parts = message.split(constants.CRLF * 2)
    assert len(message_parts) > 0
    msg_req = message_parts[0].split(constants.CRLF)
    msg_body = utils.get(message_parts, 1)  # noqa: F841
    request_line = msg_req[0]
    match = re.search(constants.REQUEST_LINE_MATCHER, request_line)
    if match:
        grouped = match.groupdict()
        headers_line = msg_req[1:]
        req = request.Request(
            resource=grouped.get("resource", ""),
            method=cast(Literal["GET", "POST"], grouped.get("method", "")),  # type: ignore
            env=env,
            header=request.Header.from_list(headers_line),
            body=msg_body,
        )
        res = app.run(req)
    else:
        res = response.response_builder(500, "Server Error").encode()
    conn.sendall(res)
    conn.close()


def get_directory_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory")
    args = parser.parse_args()
    return args.directory


if __name__ == "__main__":
    main()
