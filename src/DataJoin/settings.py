
# -*- coding: utf-8 -*-
import os

from src.DataJoin.utils import file_utils
from src.DataJoin.utils import log_utils

log_utils.LoggerFactory.set_directory(os.path.join(file_utils.get_project_base_directory(), 'logs', 'server'))
http_server_logger = log_utils.getLogger("server_stat")


API_VERSION = "v1"
SERVERS = 'servers'
SERVER_MODULE = 'route_server.py'
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
DEFAULT_GRPC_OVERALL_TIMEOUT = 60 * 1000  # ms
HEADERS = {
    'Content-Type': 'application/json',
}

IP = '0.0.0.0'
GRPC_PORT = 9360
HTTP_PORT = 9380

DATABASE = {
    'name': 'ds_pre',
    'user': 'ads_model',
    'passwd': 'ADS1model',
    'host': 'mysql-cn-north-1-642d75c2165e42e7.rds.jdcloud.com',
    'port': 3306,
    'max_connections': 100,
    'stale_timeout': 30,
}
REDIS = {
    'host': "ap2.jd.local",
    'port': 5360,
    'password': "jim://2834234004239665491/1078",
    'max_connections': 500
}
REDIS_QUEUE_DB_INDEX = 0

PROXY_DATA_HOST = "localhost"
PROXY_DATA_PORT = 9400


