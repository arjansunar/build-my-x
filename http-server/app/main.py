import socket  # noqa: F401


CRLF = "\r\n"


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, _ = server_socket.accept()  # wait for client
    response = b"HTTP/1.1 200 OK\r\n\r\n"
    conn.sendall(response)


if __name__ == "__main__":
    main()
