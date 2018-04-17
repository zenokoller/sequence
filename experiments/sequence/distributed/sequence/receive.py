import socket


def receive_sequence(port: int, reflect: bool = False):
    """Receive sequence on socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))

    while True:
        data, address = sock.recvfrom(1024)

        if not data:
            break

        if reflect:
            sock.sendto(data, address)

    sock.close()
