import re
import socket  # noqa: F401


CRLF = "\r\n"

REQUEST_MATCHER = r"(?P<method>GET|POST) (?P<target>/[\w.]*)"


def response_builder(status: int, reason_phrase: str, version="HTTP/1.1"):
    return f"{version} {status} {reason_phrase}{CRLF}{CRLF}"


AVAILABLE_ROUTES = [
    "/",
]


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, _ = server_socket.accept()  # wait for client
    message = conn.recv(1024).decode()
    request = message.split(CRLF)
    match = re.search(REQUEST_MATCHER, request[0])
    if match:
        grouped = match.groupdict()
        known_route = grouped.get("target") in AVAILABLE_ROUTES
        if not known_route:
            response = response_builder(404, "Not Found").encode()
        else:
            response = response_builder(200, "OK").encode()
    else:
        response = response_builder(500, "Server Error").encode()
    conn.sendall(response)
    conn.close()


if __name__ == "__main__":
    main()
