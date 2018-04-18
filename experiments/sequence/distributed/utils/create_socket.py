import socket


def create_socket(src_port: int = None) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if src_port is not None:
        sock.bind(('', src_port))
    return sock
