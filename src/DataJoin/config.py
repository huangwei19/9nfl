
# -*- coding: utf-8 -*-

api_version = "v1"
SLEEP_TIME = 60 * 60 * 24
HEADERS = {
    'Content-Type': 'application/json',
}

Data_Block_Suffix = '.data'
Data_Block_Meta_Suffix = '.meta'
Invalid_ExampleId = ''
Invalid_EventTime = -8223372020784275321

HTTP_SERVICE_HOST = '0.0.0.0'
HTTP_SERVICE_PORT = 9380

DATABASE = {
    'name': '',
    'user': '',
    'passwd': '',
    'host': '',
    'port': 3306,
    'max_connections': 100,
    'stale_timeout': 30,
}
REDIS = {
    'host': "",
    'port': 6379,
    'password': "",
    'max_connections': 500
}
db_index = 0

PROXY_SERVICE_HOST = "localhost"
PROXY_SERVICE_PORT = 9400
DATA_CENTER_PORT = 50052
sync_example_id_nums = 2048
removed_items_nums_from_buffer = 1024


