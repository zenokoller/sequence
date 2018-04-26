import socket


def create_socket(local_port: int = None) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if local_port is not None:
        sock.bind(('', local_port))
    return sock
