import argparse
import socket
from typing import Any, cast

from app import message


def parse_args() -> str | None:
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("--resolver")
    args = parser.parse_args()
    return cast(str | None, args.resolver)


def dns_forwarding(origin: tuple[bytes, Any], resolver: str):
    buf, source = origin
    host, port = resolver.split(":")
    origin_msg = message.DnsMessage.from_bytes(buf)
    print(f"\n\n {origin_msg=} {host=}, {port=}\n\n")
    for i in range(origin_msg.header.qcount):
        question = origin_msg.questions[i]
        print(f"\n\n {question=}\n\n")

        req_msg = message.DnsMessage(
            header=message.Header(
                id=origin_msg.header.id,
                flags=message.Flags(
                    qr=origin_msg.header.flags.qr,
                    opcode=origin_msg.header.flags.opcode,
                    aa=0,
                    tc=0,
                    rd=origin_msg.header.flags.rd,
                    ra=0,
                    z=0,
                    rcode=0 if origin_msg.header.flags.opcode == 0 else 4,
                ),
                qcount=1,
                ancount=0,
                nscount=0,
                arcount=0,
            ),
            questions=[question],
            answer=message.Answer(rrs=[]),
        )

        print(f"\n\n {req_msg=}\n\n")

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            _ = sock.sendto(req_msg.encode(), (host, port))
            response, _ = sock.recvfrom(512)
            print(f"\n\n {response=}")
            response_msg = message.DnsMessage.from_bytes(response)
            print(f"\n\n {response_msg=}")


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", 2053))

    while True:
        try:
            buf, source = udp_socket.recvfrom(512)
            msg = message.DnsMessage.from_bytes(buf)

            resolver = parse_args()
            print(f"\n\n {resolver=}\n\n")
            if resolver is not None:
                dns_forwarding(origin=(buf, source), resolver=resolver)

            print(f"\n\n Resolver: {resolver=}\n\n")

            response_msg = message.DnsMessage(
                header=message.Header(
                    id=msg.header.id,
                    flags=message.Flags(
                        qr=message.QR_REPLY_PACKET,
                        opcode=msg.header.flags.opcode,
                        aa=0,
                        tc=0,
                        rd=msg.header.flags.rd,
                        ra=0,
                        z=0,
                        rcode=0 if msg.header.flags.opcode == 0 else 4,
                    ),
                    qcount=msg.header.qcount,
                    ancount=msg.header.qcount,
                    nscount=0,
                    arcount=0,
                ),
                questions=[
                    message.Question(name=question.name) for question in msg.questions
                ],
                answer=message.Answer(
                    rrs=[
                        message.ResourceRecords(
                            name=question.name,
                            ttl=60,
                            rdata="8.8.8.8",
                        )
                        for question in msg.questions
                    ]
                ),
            )

            print(f"Received message: {msg}")
            print(f"Sending response: {response_msg}")

            response = response_msg.encode()
            udp_socket.sendto(response, source)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()
