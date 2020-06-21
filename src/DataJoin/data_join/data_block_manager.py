# coding: utf-8

import threading
import logging
import os
import uuid

import tensorflow.compat.v1 as tf
from google.protobuf import text_format
from tensorflow.compat.v1 import gfile

from DataJoin.common import data_join_service_pb2 as dj_pb

from DataJoin.data_join.common import (
    make_tf_record_iter, encode_data_block_meta_fname,
    encode_block_id, encode_data_block_fname, partition_repr
)

import requests

convert_svc = os.environ.get("DataConvert_Svc")


def res_convert_tf_into_pw(meta_path, block_path):
    HEADERS = {
        'Content-Type': 'application/json',
    }
    action = getattr(requests, 'POST'.lower(), None)

    data = {'dfs_data_block_meta': meta_path, 'dfs_data_block': block_path}

    url = "http://{0}:9380/v1/parse/data/block/meta".format(str(convert_svc))

    response = action(url=url, json=data, headers=HEADERS)

    res = response.json()
    logging.info('request result is :%s' % res)


class DataBlockMaker(object):
    TMP_COUNTER = 0

    def __init__(self, dirname, data_source_name, partition_id,
                 data_block_index, max_example_num=None):
        self._data_source_name = data_source_name
        self._partition_id = partition_id
        self._max_example_num = max_example_num
        self._dirname = dirname
        self._tmp_fpath = self._get_tmp_fpath()
        self._tf_record_writer = tf.io.TFRecordWriter(self._tmp_fpath)
        self._data_block_meta = dj_pb.DataBlockMeta()
        self._data_block_meta.partition_id = partition_id
        self._data_block_meta.data_block_index = data_block_index
        self._data_block_meta.follower_restart_index = 0
        self._example_num = 0
        self._data_block_manager = None

    def init_by_meta(self, meta):
        self._partition_id = meta.partition_id
        self._max_example_num = None
        self._data_block_meta = meta

    def set_data_block_manager(self, data_block_manager):
        self._data_block_manager = data_block_manager

    def append(self, record, example_id, event_time):
        self._tf_record_writer.write(record)
        self._data_block_meta.example_ids.append(example_id)
        if self._example_num == 0:
            self._data_block_meta.start_time = event_time
            self._data_block_meta.end_time = event_time
        else:
            if event_time < self._data_block_meta.start_time:
                self._data_block_meta.start_time = event_time
            if event_time > self._data_block_meta.end_time:
                self._data_block_meta.end_time = event_time

        self._example_num += 1

    def set_follower_restart_index(self, follower_restart_index):
        self._data_block_meta.follower_restart_index = follower_restart_index

    def append_raw_example(self, record):
        self._tf_record_writer.write(record)
        self._example_num += 1

    def check_data_block_full(self):
        if (self._max_example_num is not None and
                len(self._data_block_meta.example_ids) >=
                self._max_example_num):
            return True
        return False

    def get_data_block_meta(self):
        if len(self._data_block_meta.example_ids) > 0:
            return self._data_block_meta
        return None

    def get_leader_begin_index(self):
        return self._leader_begin_index

    def example_count(self):
        return len(self._data_block_meta.example_ids)

    def finish_data_block(self):
        assert self._example_num == len(self._data_block_meta.example_ids)
        self._tf_record_writer.close()
        if len(self._data_block_meta.example_ids) > 0:
            self._data_block_meta.block_id = \
                encode_block_id(self._data_source_name,
                                self._data_block_meta)
            data_block_path = os.path.join(
                self._get_data_block_dir(),
                encode_data_block_fname(
                    self._data_source_name,
                    self._data_block_meta
                )
            )
            gfile.Rename(self._tmp_fpath, data_block_path, True)
            meta_path = self._build_data_block_meta()
            # todo: request convert tfrecord  into vw api
            # res_convert_tf_into_pw(meta_path, data_block_path)
            return self._data_block_meta
        gfile.Remove(self._tmp_fpath)
        return None

    def _get_data_block_dir(self):
        return os.path.join(
            self._dirname, partition_repr(self._partition_id)
        )

    def _get_tmp_fpath(self):
        tmp_fname = str(uuid.uuid1()) + '-{}.tmp'.format(self.TMP_COUNTER)
        self.TMP_COUNTER += 1
        return os.path.join(self._get_data_block_dir(), tmp_fname)

    def _build_data_block_meta(self):
        tmp_meta_fpath = self._get_tmp_fpath()
        meta = self._data_block_meta
        with tf.io.TFRecordWriter(tmp_meta_fpath) as meta_writer:
            meta_writer.write(text_format.MessageToString(meta).encode())
        if self._data_block_manager is not None:
            meta_fpath = self._data_block_manager.commit_data_block_meta(
                tmp_meta_fpath, meta
            )
        else:
            meta_fname = encode_data_block_meta_fname(self._data_source_name,
                                                      self._partition_id,
                                                      meta.data_block_index)
            meta_fpath = os.path.join(self._get_data_block_dir(), meta_fname)
            gfile.Rename(tmp_meta_fpath, meta_fpath)
        return meta_fpath

    def __del__(self):
        if self._tf_record_writer is not None:
            del self._tf_record_writer


class DataBlockManager(object):
    def __init__(self, partition_id, data_block_dir, data_source_name):
        self._lock = threading.Lock()
        self._partition_id = partition_id
        self._data_block_dir = data_block_dir
        self._data_source_name = data_source_name
        self._data_block_meta_cache = {}
        self._dumped_index = None
        self._dumping_index = None
        self._make_data_block_dir_if_no_existed()
        self._sync_dumped_index()

    def acquire_produced_data_block_number(self):
        with self._lock:
            self._sync_dumped_index()
            return self._dumped_index + 1

    def get_data_block_meta_by_index(self, index):
        with self._lock:
            if index < 0:
                raise IndexError("{} index out of range".format(index))
            self._sync_dumped_index()
            return self._sync_data_block_meta(index)

    def get_lastest_data_block_meta(self):
        with self._lock:
            self._sync_dumped_index()
            return self._sync_data_block_meta(self._dumped_index)

    def commit_data_block_meta(self, tmp_meta_fpath, data_block_meta):
        if not gfile.Exists(tmp_meta_fpath):
            raise RuntimeError("the tmp file is not existed {}" \
                               .format(tmp_meta_fpath))
        with self._lock:
            if self._dumping_index is not None:
                raise RuntimeError(
                    "data block with index {} is " \
                    "dumping".format(self._dumping_index)
                )
            data_block_index = data_block_meta.data_block_index
            if data_block_index != self._dumped_index + 1:
                raise IndexError("the data block index shoud be consecutive")
            self._dumping_index = data_block_index
            meta_fpath = self._get_data_block_meta_path(data_block_index)
            gfile.Rename(tmp_meta_fpath, meta_fpath)
            self._dumping_index = None
            self._dumped_index = data_block_index
            self._evict_data_block_cache_if_full()
            self._data_block_meta_cache[data_block_index] = data_block_meta
            return meta_fpath

    def _sync_dumped_index(self):
        if self._dumped_index is None:
            assert self._dumping_index is None, \
                "no index is dumping when no dumped index"
            left_index = 0
            right_index = 1 << 63
            while left_index <= right_index:
                index = (left_index + right_index) // 2
                fname = self._get_data_block_meta_path(index)
                if gfile.Exists(fname):
                    left_index = index + 1
                else:
                    right_index = index - 1
            self._dumped_index = right_index
        elif self._dumping_index is not None:
            assert self._dumping_index == self._dumped_index + 1, \
                "the dumping index shoud be next of dumped index " \
                "{} != {} + 1".format(self._dumping_index, self._dumped_index)
            fpath = self._get_data_block_meta_path(self._dumping_index)
            if not gfile.Exists(fpath):
                self._dumping_index = None
            else:
                self._dumped_index = self._dumping_index
                self._dumping_index = None

    def _make_data_block_dir_if_no_existed(self):
        encoded_data_block_dir = self._encode_data_block_dir()
        if not gfile.Exists(encoded_data_block_dir):
            gfile.MakeDirs(encoded_data_block_dir)
        if not gfile.IsDirectory(encoded_data_block_dir):
            logging.fatal("%s should be directory", encoded_data_block_dir)
            os._exit(-1)  # pylint: disable=protected-access

    def _sync_data_block_meta(self, index):
        if self._dumped_index < 0 or index > self._dumped_index:
            return None
        if index not in self._data_block_meta_cache:
            fpath = self._get_data_block_meta_path(index)
            with make_tf_record_iter(fpath) as record_iter:
                self._data_block_meta_cache[index] = \
                    text_format.Parse(next(record_iter),
                                      dj_pb.DataBlockMeta())
            self._evict_data_block_cache_if_full()
        return self._data_block_meta_cache[index]

    def _get_data_block_meta_path(self, data_block_index):
        meta_fname = encode_data_block_meta_fname(
            self._data_source_name,
            self._partition_id, data_block_index
        )
        return os.path.join(self._encode_data_block_dir(), meta_fname)

    def _encode_data_block_dir(self):
        return os.path.join(self._data_block_dir,
                            partition_repr(self._partition_id))

    def _evict_data_block_cache_if_full(self):
        while len(self._data_block_meta_cache) > 1024:
            self._data_block_meta_cache.popitem()

