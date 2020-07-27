import operator
import os
import logging
from contextlib import contextmanager
import traceback
import tensorflow.compat.v1 as tf
from DataJoin.db.db_models import DB, DataBlockMeta, DataSourceMeta, DataSource, Coordinator
from DataJoin.config import Data_Block_Suffix, Data_Block_Meta_Suffix


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


@contextmanager
def tf_record_iterator_factory(data_path):
    tf_iterator = None
    try:
        tf_iterator = tf.io.tf_record_iterator(data_path)
        yield tf_iterator
    except Exception as e:
        logging.error("build tf_record_iterator Failed file_path:{0}".format(data_path))
        traceback.print_exc(str(e))
    if tf_iterator is not None:
        del tf_iterator


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


def partition_id_wrap(partition_id):
    return 'partition_{:04}'.format(partition_id)


def data_block_meta_file_name_wrap(data_source_name,
                                   partition_id,
                                   data_block_index):
    return '{}.{}.{:08}{}'.format(
        data_source_name, partition_id_wrap(partition_id),
        data_block_index, Data_Block_Meta_Suffix
    )


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


def block_id_wrap(data_source_name, meta):
    return '{}.{}.{:08}.{}-{}'.format(
        data_source_name, partition_id_wrap(meta.partition_id),
        meta.data_block_index, meta.start_time, meta.end_time
    )


def data_block_file_name_wrap(data_source_name, meta):
    block_id = block_id_wrap(data_source_name, meta)
    return '{}{}'.format(block_id, Data_Block_Suffix)
