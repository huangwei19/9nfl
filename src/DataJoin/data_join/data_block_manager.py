# coding: utf-8

import threading
import logging
import os
import uuid

import tensorflow.compat.v1 as tf
from google.protobuf import text_format
from tensorflow.compat.v1 import gfile

from DataJoin.common import data_join_service_pb2 as dj_pb

from DataJoin.utils.data_process import tf_record_iterator_factory, data_block_meta_file_name_wrap, \
    block_id_wrap, data_block_file_name_wrap, partition_id_wrap

from DataJoin.utils.base import get_host_ip
import requests
from DataJoin.config import HEADERS, HTTP_SERVICE_PORT

host_ip = get_host_ip()
mode = os.environ.get("MODE", None)


def save_data_block_info(meta_path, block_path):
    action = getattr(requests, 'POST'.lower(), None)
    data = {'dfs_data_block_meta': meta_path, 'dfs_data_block': block_path}
    url = "http://{0}:{1}/v1/parse/data/block/meta".format(str(host_ip), HTTP_SERVICE_PORT)
    response = action(url=url, json=data, headers=HEADERS)
    res = response.json()
    logging.info('request result is :%s' % res)


class DataBlockMaker(object):
    tmp_file_path_counter = 0

    def __init__(self, data_block_dir_name, data_source_name, partition_id,
                 data_block_index, example_num_threshold=None):
        self._data_source_name = data_source_name
        self._partition_id = partition_id
        self._example_num_threshold = example_num_threshold
        self._data_block_dir_name = data_block_dir_name
        self._tmp_file_path = self._make_tmp_file_path()
        self._tf_record_writer = tf.io.TFRecordWriter(self._tmp_file_path)
        self._data_block_meta = dj_pb.DataBlockMeta()
        self._data_block_meta.partition_id = partition_id
        self._data_block_meta.data_block_index = data_block_index
        self._data_block_meta.follower_restart_index = 0
        self._saved_example_num = 0
        self._data_block_manager = None

    def init_maker_by_input_meta(self, data_block_meta):
        self._partition_id = data_block_meta.partition_id
        self._example_num_threshold = None
        self._data_block_meta = data_block_meta

    def build_data_block_manager(self, data_block_manager):
        self._data_block_manager = data_block_manager

    def save(self, data_record, example_id, event_time):
        self._tf_record_writer.write(data_record)
        self._data_block_meta.example_ids.append(example_id)
        if self._saved_example_num == 0:
            self._data_block_meta.start_time = event_time
            self._data_block_meta.end_time = event_time
        else:
            if event_time < self._data_block_meta.start_time:
                self._data_block_meta.start_time = event_time
            if event_time > self._data_block_meta.end_time:
                self._data_block_meta.end_time = event_time

        self._saved_example_num += 1

    def set_follower_restart_index(self, follower_restart_index):
        self._data_block_meta.follower_restart_index = follower_restart_index

    def save_data_record(self, record):
        self._tf_record_writer.write(record)
        self._saved_example_num += 1

    def is_data_block_exceed_threshold(self):
        if (self._example_num_threshold is not None and
                len(self._data_block_meta.example_ids) >=
                self._example_num_threshold):
            return True
        return False

    def data_block_finalizer(self):
        assert self._saved_example_num == len(self._data_block_meta.example_ids)
        self._tf_record_writer.close()
        if len(self._data_block_meta.example_ids) > 0:
            self._data_block_meta.block_id = \
                block_id_wrap(self._data_source_name,
                              self._data_block_meta)
            data_block_path = os.path.join(
                self._obtain_data_block_dir(),
                data_block_file_name_wrap(
                    self._data_source_name,
                    self._data_block_meta
                )
            )
            gfile.Rename(self._tmp_file_path, data_block_path, True)
            meta_path = self._make_data_block_meta()
            if mode == "distribute":
                save_data_block_info(meta_path, data_block_path)
            return self._data_block_meta
        gfile.Remove(self._tmp_file_path)
        return None

    def _obtain_data_block_dir(self):
        return os.path.join(
            self._data_block_dir_name, partition_id_wrap(self._partition_id)
        )

    def _make_tmp_file_path(self):
        tmp_file_name = str(uuid.uuid1()) + '-{}.tmp'.format(self.tmp_file_path_counter)
        self.tmp_file_path_counter += 1
        return os.path.join(self._obtain_data_block_dir(), tmp_file_name)

    def _make_data_block_meta(self):
        meta_file_path_tmp = self._make_tmp_file_path()
        with tf.io.TFRecordWriter(meta_file_path_tmp) as meta_writer:
            meta_writer.write(text_format.MessageToString(self._data_block_meta).encode())
        if self._data_block_manager is not None:
            meta_file_path = self._data_block_manager.update_data_block_meta(
                meta_file_path_tmp, self._data_block_meta
            )
        else:
            meta_file_name = data_block_meta_file_name_wrap(self._data_source_name,
                                                            self._partition_id,
                                                            self._data_block_meta.data_block_index)
            meta_file_path = os.path.join(self._obtain_data_block_dir(), meta_file_name)
            gfile.Rename(meta_file_path_tmp, meta_file_path)
        return meta_file_path

    def __del__(self):
        if self._tf_record_writer is not None:
            del self._tf_record_writer


class DataBlockManager(object):
    def __init__(self, partition_id, data_block_dir, data_source_name):
        self._lock = threading.Lock()
        self._partition_id = partition_id
        self._data_block_dir = data_block_dir
        self._data_source_name = data_source_name
        self._data_block_meta_memory_buffer = dict()
        self._saved_data_block_index = None
        self._saving_data_block_index = None
        self._create_data_block_dir_if_need()
        self._sync_saved_data_block_index()

    def acquire_produced_data_block_number(self):
        with self._lock:
            self._sync_saved_data_block_index()
            return self._saved_data_block_index + 1

    def acquire_data_block_meta_by_index(self, index):
        with self._lock:
            if index < 0:
                raise IndexError("{} index is not in range".format(index))
            self._sync_saved_data_block_index()
            return self._sync_data_block_meta(index)

    def update_data_block_meta(self, meta_file_path_tmp, data_block_meta):
        if not gfile.Exists(meta_file_path_tmp):
            raise RuntimeError("the tmp file no existed {}".format(meta_file_path_tmp))
        with self._lock:
            if self._saving_data_block_index is not None:
                raise RuntimeError(
                    "data block of index {} is " \
                    "saving".format(self._saving_data_block_index)
                )
            data_block_index = data_block_meta.data_block_index
            if data_block_index != self._saved_data_block_index + 1:
                raise IndexError("the data_block_index must be consecutive")
            self._saving_data_block_index = data_block_index
            data_block_meta_path = self._acquire_data_block_meta_path(data_block_index)
            gfile.Rename(meta_file_path_tmp, data_block_meta_path)
            self._saving_data_block_index = None
            self._saved_data_block_index = data_block_index
            self._remove_item_from_data_block_memory_buffer()
            self._data_block_meta_memory_buffer[data_block_index] = data_block_meta
            return data_block_meta_path

    def _sync_saved_data_block_index(self):
        if self._saved_data_block_index is None:
            assert self._saving_data_block_index is None, \
                "no data block index is saving when no saved index"
            low_index = 0
            high_index = 1 << 63
            while low_index <= high_index:
                index = (low_index + high_index) // 2
                file_name = self._acquire_data_block_meta_path(index)
                if gfile.Exists(file_name):
                    low_index = index + 1
                else:
                    high_index = index - 1
            self._saved_data_block_index = high_index
        elif self._saving_data_block_index is not None:
            assert self._saving_data_block_index == self._saved_data_block_index + 1, \
                "the saving index should be next of saved index " \
                "{} != {} + 1".format(self._saving_data_block_index, self._saved_data_block_index)
            file_name = self._acquire_data_block_meta_path(self._saving_data_block_index)
            if not gfile.Exists(file_name):
                self._saving_data_block_index = None
            else:
                self._saved_data_block_index = self._saving_data_block_index
                self._saving_data_block_index = None

    def _create_data_block_dir_if_need(self):
        data_block_dir_wrap = self._data_block_dir_wrap()
        if not gfile.Exists(data_block_dir_wrap):
            gfile.MakeDirs(data_block_dir_wrap)
        if not gfile.IsDirectory(data_block_dir_wrap):
            logging.fatal("%s must be directory", data_block_dir_wrap)
            os._exit(-1)

    def _sync_data_block_meta(self, index):
        if self._saved_data_block_index < 0 or index > self._saved_data_block_index:
            return None
        if index not in self._data_block_meta_memory_buffer:
            data_block_meta_file_path = self._acquire_data_block_meta_path(index)
            with tf_record_iterator_factory(data_block_meta_file_path) as record_iter:
                self._data_block_meta_memory_buffer[index] = \
                    text_format.Parse(next(record_iter),
                                      dj_pb.DataBlockMeta())
            self._remove_item_from_data_block_memory_buffer()
        return self._data_block_meta_memory_buffer[index]

    def _acquire_data_block_meta_path(self, data_block_index):
        data_block_meta_file_name = data_block_meta_file_name_wrap(
            self._data_source_name,
            self._partition_id, data_block_index
        )
        return os.path.join(self._data_block_dir_wrap(), data_block_meta_file_name)

    def _data_block_dir_wrap(self):
        return os.path.join(self._data_block_dir,
                            partition_id_wrap(self._partition_id))

    def _remove_item_from_data_block_memory_buffer(self):
        while len(self._data_block_meta_memory_buffer) > 1024:
            self._data_block_meta_memory_buffer.popitem()
