import time
import socket
import logging


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def current_timestamp():
    return int(time.time() * 1000)


def address_valid_checker(address):
    try:
        (ip, port_str) = address.split(':')
        if ip == 'localhost' or (socket.inet_aton(ip) and ip.count('.') == 3):
            port = int(port_str)
            if 0 <= port <= 65535:
                return True
        return False
    except Exception as e:
        logging.info('{0} is not valid address. error: is {1}.'.format(address, str(e)))
    return False
