import os


def get_src_ip():
    return os.popen('ifconfig eth0').read().split('inet addr:')[1].split()[0]
