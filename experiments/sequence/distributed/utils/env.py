import os

CLIENT_IP_NAME = 'CLIENT_DOMAIN_CLIENT_ADDR'
SERVER_IP_NAME = 'SERVER_DOMAIN_SERVER_ADDR'
LOCALHOST = '127.0.0.1'


def get_client_ip() -> str:
    return os.environ.get(CLIENT_IP_NAME, LOCALHOST)


def get_server_ip() -> str:
    return os.environ.get(SERVER_IP_NAME, LOCALHOST)
