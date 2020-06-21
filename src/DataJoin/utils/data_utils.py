
import operator
import threading
from DataJoin.db.db_models import DB, DataBlockMeta, DataSourceMeta, DataSource, Coordinator


class IdCounter:
    _lock = threading.RLock()

    def __init__(self, initial_value=0):
        self._value = initial_value

    def incr(self, delta=1):
        '''
        Increment the counter with locking
        '''
        with IdCounter._lock:
            self._value += delta
            return self._value


id_counter = IdCounter()


def query_data_block_meta(**kwargs):
    with DB.connection_context():
        filters = []
        for f_n, f_v in kwargs.items():
            attr_name = '%s' % f_n
            if hasattr(DataBlockMeta, attr_name):
                if attr_name == "start_time":
                    filters.append(operator.attrgetter('%s' % f_n)(DataBlockMeta) >= f_v)
                elif attr_name == "end_time":
                    filters.append(operator.attrgetter('%s' % f_n)(DataBlockMeta) <= f_v)
                else:
                    filters.append(operator.attrgetter('%s' % f_n)(DataBlockMeta) == f_v)
        if filters:
            data_block_metas = DataBlockMeta.select(DataBlockMeta.block_id, DataBlockMeta.data_block_index,
                                                    DataBlockMeta.dfs_data_block_dir, DataBlockMeta.start_time,
                                                    DataBlockMeta.end_time, DataBlockMeta.leader_end_index,
                                                    DataBlockMeta.leader_start_index,
                                                    DataBlockMeta.follower_restart_index, DataBlockMeta.partition_id,
                                                    DataBlockMeta.file_version).where(*filters)
        else:
            data_block_metas = DataBlockMeta.select(DataBlockMeta.block_id, DataBlockMeta.data_block_index,
                                                    DataBlockMeta.dfs_data_block_dir, DataBlockMeta.start_time,
                                                    DataBlockMeta.end_time, DataBlockMeta.leader_end_index,
                                                    DataBlockMeta.leader_start_index,
                                                    DataBlockMeta.follower_restart_index, DataBlockMeta.partition_id,
                                                    DataBlockMeta.file_version)
        return [data_block_meta for data_block_meta in data_block_metas]


def batch_update_data_block_meta(**kwargs):
    with DB.connection_context():
        filters = []
        for f_n, f_v in kwargs["filters"].items():
            attr_name = '%s' % f_n
            if hasattr(DataBlockMeta, attr_name):
                if attr_name == "start_time":
                    filters.append(operator.attrgetter('%s' % f_n)(DataBlockMeta) >= f_v)
                elif attr_name == "end_time":
                    filters.append(operator.attrgetter('%s' % f_n)(DataBlockMeta) <= f_v)
                else:
                    pass
        DataBlockMeta.update(kwargs["updated"]).where(*filters)


def query_data_source_meta(**kwargs):
    with DB.connection_context():
        filters = []
        for f_n, f_v in kwargs.items():
            attr_name = '%s' % f_n
            if hasattr(DataSourceMeta, attr_name):
                filters.append(operator.attrgetter('%s' % f_n)(DataSourceMeta) == f_v)
        if filters:
            data_source_metas = DataSourceMeta.select().where(*filters)
        else:
            data_source_metas = DataSourceMeta.select()
        return [data_source_meta for data_source_meta in data_source_metas]


def query_data_source(**kwargs):
    with DB.connection_context():
        filters = []
        for f_n, f_v in kwargs.items():
            attr_name = '%s' % f_n
            if hasattr(DataSource, attr_name):
                filters.append(operator.attrgetter('%s' % f_n)(DataSource) == f_v)
        if filters:
            data_sources = DataSource.select().where(*filters)
        else:
            data_sources = DataSource.select()
        return [data_source for data_source in data_sources]


def query_coordinator_info(**kwargs):
    with DB.connection_context():
        filters = []
        for f_n, f_v in kwargs.items():
            attr_name = '%s' % f_n
            if hasattr(Coordinator, attr_name):
                filters.append(operator.attrgetter('%s' % f_n)(Coordinator) == f_v)
        if filters:
            coordinators = Coordinator.select().where(*filters)
        else:
            coordinators = Coordinator.select()
        return [coordinator for coordinator in coordinators]

