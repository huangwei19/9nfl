
# -*- coding: utf-8 -*-

api_version = "v1"
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
HEADERS = {
    'Content-Type': 'application/json',
}

Data_Block_Suffix = '.data'
Data_Block_Meta_Suffix = '.meta'
Invalid_ExampleId = ''
Invalid_EventTime = -8223372020784275321

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
    'host': "10.186.8.219",
    'port': 6379,
    'password': "",
    'max_connections': 500
}
db_index = 0

PROXY_DATA_HOST = "localhost"
PROXY_DATA_PORT = 9400
DATA_CENTER_PORT = 50052


