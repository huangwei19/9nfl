
import os

from DataJoin.settings import REDIS, REDIS_QUEUE_DB_INDEX
import redis
from DataJoin.settings import http_server_logger


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        key = str(cls) + str(os.getpid())
        if key not in instances:
            instances[key] = cls(*args, **kw)
        return instances[key]

    return _singleton


@singleton
class RedisManage(object):
    def __init__(self):
        config = REDIS.copy()
        self.pool = redis.ConnectionPool(host=config['host'], port=config['port'], password=config['password'], \
             max_connections=config['max_connections'], db=REDIS_QUEUE_DB_INDEX)
        http_server_logger.info('init redis connection pool.')

    def get_conn(self):
        return redis.Redis(connection_pool=self.pool, decode_responses=True)

    def get(self, key):
        try:
            conn = self.get_conn()
            value = conn.get(key)
            if value:
                http_server_logger.info('get from redis, {}:{}'.format(key, value))
                return True, value
            else:
                http_server_logger.info('get from redis return nil, key={}'.format(key))
                return False,value
        except Exception as e:
            http_server_logger.exception(e)
            http_server_logger.error('get from redis failed')
            return None

    def setex(self, key, value, expire_seconds=108000*24*5):
        try:
            conn = self.get_conn()
            conn.setex(key, expire_seconds, value)
            http_server_logger.info('set {}:{} {} into redis.'.format(key, value, expire_seconds))
        except Exception as e:
            http_server_logger.exception(e)
            http_server_logger.info('set {}:{} {} into redis failed.'.format(key, value, expire_seconds))

    def delete(self, *key):
        try:
            conn = self.get_conn()
            conn.delete(*key)
            http_server_logger.info('del {} from redis.'.format(*key))
        except Exception as e:
            http_server_logger.exception(e)
            http_server_logger.info('del {} from redis failed.'.format(*key))


