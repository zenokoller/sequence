import os
from typing import Tuple

CLIENT_IP_NAME = 'CLIENT_DOMAIN_CLIENT_ADDR'
SERVER_IP_NAME = 'SERVER_DOMAIN_SERVER_ADDR'
LOCALHOST = '127.0.0.1'


def get_client_host() -> str:
    return os.environ.get(CLIENT_IP_NAME, LOCALHOST)


def get_server_host() -> str:
    return os.environ.get(SERVER_IP_NAME, LOCALHOST)


def parse_server_addr(addr: str) -> Tuple[str, int]:
    first, *second = addr.split(':')
    if len(second) > 0:
        return first, int(second[0])
    else:
        return get_server_host(), int(first)
