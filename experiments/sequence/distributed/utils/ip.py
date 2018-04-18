import os


def get_my_ip():
    if os.environ.get('LOCAL'):
        return '127.0.0.1'

    try:  # Alpine
        return os.popen('ifconfig eth0').read().split('inet addr:')[1].split()[0]
    except IndexError:
        pass

    try:  # macOS
        return os.popen('ifconfig en0').read().split('inet ')[1].split()[0]
    except IndexError:
        pass
