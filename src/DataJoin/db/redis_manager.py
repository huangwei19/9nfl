import os
from DataJoin.settings import REDIS, db_index
import redis
import logging
import traceback
import sys


def singleton(cls, *args, **kw):
    _registry = dict()

    def _singleton():
        key = str(cls) + str(os.getpid())
        if key not in _registry:
            _registry[key] = cls(*args, **kw)
        return _registry[key]

    return _singleton


@singleton
class RedisManage(object):
    def __init__(self):
        redis_conf = REDIS.copy()
        self.redis_pool = redis.ConnectionPool(host=redis_conf['host'], port=redis_conf['port'],
                                               password=redis_conf['password'], \
                                               max_connections=redis_conf['max_connections'], db=db_index)
        logging.info('init redis connection pool successfully.')

    def acquire_redis_conn(self):
        return redis.Redis(connection_pool=self.redis_pool, decode_responses=True)

    def get(self, key):
        try:
            redis_conn = self.acquire_redis_conn()
            value = redis_conn.get(key)
            if value:
                logging.info('get from redis, {}:{}'.format(key, value))
                return True, value
            else:
                logging.info('get from redis return nul, key={}'.format(key))
                return False, value
        except Exception as e:
            logging.error('get value from redis failed')
            traceback.print_exc(file=sys.stdout)
            return None

    def set(self, key, value, expire_seconds=108000 * 24 * 5):
        try:
            redis_conn = self.acquire_redis_conn()
            redis_conn.setex(key, expire_seconds, value)
            logging.info('set {}:{} {} into redis.'.format(key, value, expire_seconds))
        except Exception as e:
            logging.info('set {}:{} {} into redis failed.'.format(key, value, expire_seconds))
            traceback.print_exc(file=sys.stdout)

    def delete(self, *key):
        try:
            redis_conn = self.acquire_redis_conn()
            redis_conn.delete(*key)
            logging.info('del {} from redis.'.format(*key))
        except Exception as e:
            logging.info('del {} from redis failed.'.format(*key))
            traceback.print_exc(file=sys.stdout)
