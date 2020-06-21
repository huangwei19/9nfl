import datetime
import inspect
import os
import sys

import __main__
from peewee import Model, CharField, IntegerField, BigIntegerField, TextField, CompositeKey
from playhouse.pool import PooledMySQLDatabase

from DataJoin.utils import log_utils
from DataJoin.utils.core import current_timestamp
from DataJoin.settings import DATABASE, http_server_logger

LOGGER = log_utils.getLogger()


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        key = str(cls) + str(os.getpid())
        if key not in instances:
            instances[key] = cls(*args, **kw)
        return instances[key]

    return _singleton


@singleton
class BaseDataBase(object):
    def __init__(self):
        database_config = DATABASE.copy()
        db_name = database_config.pop("name")
        self.database_connection = PooledMySQLDatabase(db_name, **database_config)
        http_server_logger.info('init mysql database on standalone mode successfully')


if __main__.__file__.endswith('route_server.py'):
    DB = BaseDataBase().database_connection
else:
    # Initialize the database only when the server is started.
    DB = None


def close_connection(db_connection):
    try:
        if db_connection:
            db_connection.close()
    except Exception as e:
        LOGGER.exception(e)


class DataBaseModel(Model):
    class Meta:
        database = DB

    def to_json(self):
        return self.__dict__['__data__']

    def save(self, *args, **kwargs):
        if hasattr(self, "update_date"):
            self.update_date = datetime.datetime.now()
        if hasattr(self, "update_time"):
            self.update_time = current_timestamp()
        super(DataBaseModel, self).save(*args, **kwargs)


def init_database_tables():
    with DB.connection_context():
        members = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        table_objs = []
        for name, obj in members:
            if obj != DataBaseModel and issubclass(obj, DataBaseModel):
                table_objs.append(obj)
        DB.create_tables(table_objs)


class DataBlockMeta(DataBaseModel):
    block_id = CharField(max_length=100)
    dfs_data_block_dir = CharField(max_length=100)
    partition_id = IntegerField(null=True, default=0)
    file_version = IntegerField(null=True, default=0)
    start_time = BigIntegerField(null=True)
    end_time = BigIntegerField(null=True)
    example_ids = TextField(null=True, default='')
    leader_start_index = BigIntegerField(null=True)
    leader_end_index = BigIntegerField(null=True)
    follower_start_index = BigIntegerField(null=True)
    follower_end_index = BigIntegerField(null=True)
    data_block_index = BigIntegerField(null=True)
    follower_restart_index = BigIntegerField(null=True)
    create_time = BigIntegerField(null=True)
    update_time = BigIntegerField(null=True)
    create_status = IntegerField(null=True, default=0)  # 1:creating,2:success 3: failed
    consumed_status = IntegerField(null=True, default=0)  # 1:未消费 2：已消费
    data_source_name = CharField(max_length=300)
    class Meta:
        db_table = "data_block_meta"
        primary_key = CompositeKey('block_id')


class DataSourceMeta(DataBaseModel):
    data_source_name = CharField(max_length=100)
    partition_num = IntegerField(null=True, default=0)
    matching_window = BigIntegerField(null=True)
    data_source_type = IntegerField(null=True)
    max_example_in_data_block = BigIntegerField(null=True)
    inherit_data_source = CharField(max_length=100)
    start_time = BigIntegerField(null=True)
    end_time = BigIntegerField(null=True)
    create_time = BigIntegerField(null=True)
    update_time = BigIntegerField(null=True)

    class Meta:
        db_table = "data_source_meta"
        primary_key = CompositeKey('data_source_name')


class DataSource(DataBaseModel):
    data_source_name = CharField(max_length=100)
    dfs_data_block_dir = CharField(max_length=100)
    dfs_raw_data_dir = CharField(max_length=100)
    data_source_role = IntegerField(null=True, default=0)
    data_source_state = IntegerField(null=True, default=0)
    start_time = BigIntegerField(null=True)
    end_time = BigIntegerField(null=True)
    create_time = BigIntegerField(null=True)
    update_time = BigIntegerField(null=True)

    class Meta:
        db_table = "data_source"
        primary_key = CompositeKey('data_source_name')


class Coordinator(DataBaseModel):
    ip_port = CharField(max_length=100)
    register_code = IntegerField(null=True, default=0)  # 1:注册成功 2：注册失败
    query_code = IntegerField(null=True, default=0)  # 1:查询成功 2: 查询失败
    local_uuid = CharField(max_length=100)
    remote_uuid = CharField(max_length=100)
    create_time = BigIntegerField(null=True)
    update_time = BigIntegerField(null=True)

    class Meta:
        db_table = "register_coordinator"
        primary_key = CompositeKey('local_uuid')
