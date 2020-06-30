import logging
import os
from DataJoin.db.redis_manager import RedisManage

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    redis_cli = RedisManage()
    remote_ip = None
    host_ip = None
    while not remote_ip:
        remote_ip = os.environ.get("REMOTE_IP", None)
    get_status, result = redis_cli.get(remote_ip)
    if get_status:
        redis_cli.delete(remote_ip)
    while not host_ip:
        host_ip = os.environ.get("HOST_IP", None)
    redis_cli.setex(remote_ip, "{0}:7001".format(os.environ.get("HOST_IP", None)))
