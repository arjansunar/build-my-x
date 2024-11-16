import socket

from app import message


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", 2053))

    while True:
        try:
            buf, source = udp_socket.recvfrom(512)
            msg = message.DnsMessage.from_bytes(buf)
            example_response = message.DnsMessage(
                header=message.Header(
                    id=msg.header.id,
                    flags=message.Flags(
                        qr=message.QR_REPLY_PACKET,
                        opcode=0,
                        aa=0,
                        tc=0,
                        rd=0,
                        ra=0,
                        z=0,
                        rcode=0,
                    ),
                    qcount=1,
                    ancount=0,
                    nscount=0,
                    arcount=0,
                ),
                question=message.Question(name="codecrafters.io"),
            )

            response = example_response.encode()
            udp_socket.sendto(response, source)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()
