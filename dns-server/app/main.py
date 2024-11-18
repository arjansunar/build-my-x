import argparse
import socket
from typing import cast

from app import message


def parse_args() -> str | None:
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("--resolver")
    args = parser.parse_args()
    return cast(str | None, args.resolver)


def dns_forwarding(buf: bytes, resolver: str):
    host, port = resolver.split(":")
    port = int(port)
    origin_msg = message.DnsMessage.from_bytes(buf)
    origin_msg.header.qcount = 1  # resolver can only handle one question at a time
    answer = message.Answer([])
    for question in origin_msg.questions:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            req = b"".join(
                [
                    origin_msg.header.encode(),
                    question.encode(),
                ]
            )
            _ = sock.sendto(
                req,
                (host, port),
            )
            response, _ = sock.recvfrom(512)
            response_msg = message.DnsMessage.from_bytes(response)
            if len(response_msg.answer.rrs) == 0:
                continue
            answer.rrs.append(response_msg.answer.rrs[0])

    return message.DnsMessage(
        header=message.Header(
            id=origin_msg.header.id,
            flags=message.Flags(
                qr=message.QR_REPLY_PACKET,
                opcode=origin_msg.header.flags.opcode,
                aa=0,
                tc=0,
                rd=origin_msg.header.flags.rd,
                ra=0,
                z=0,
                rcode=0 if origin_msg.header.flags.opcode == 0 else 4,
            ),
            qcount=len(origin_msg.questions),
            ancount=len(answer.rrs),
            nscount=0,
            arcount=0,
        ),
        questions=origin_msg.questions,
        answer=answer,
    )


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
            if resolver is not None:
                response_msg = dns_forwarding(buf=buf, resolver=resolver)
            else:
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
                        message.Question(name=question.name)
                        for question in msg.questions
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
