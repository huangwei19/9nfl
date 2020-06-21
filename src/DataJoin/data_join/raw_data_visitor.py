# coding: utf-8

import logging
from DataJoin.data_join import common
from DataJoin.data_join.raw_data_iter_impl.raw_data_iter import DataIterator
from DataJoin.data_join.raw_data_iter_impl.tf_record_iter import TfRecordDataIterator
from os import path
from tensorflow.compat.v1 import gfile
import uuid
import os


class RawDataManager(object):
    def __init__(self, raw_data_dir, raw_data_options, mode):
        self._raw_data_dir = raw_data_dir
        self._raw_data_options = raw_data_options
        self._local_raw_dat_dir = None
        self.mode = mode
        self.encode_local_raw_data_dir()
        self._all_fpath = None
        self._preload_raw_data_file_path()
        self.item_dict = dict()
        self.raw_data_stale = False
        self._load_raw_data_to_mem()

    def encode_local_raw_data_dir(self):
        self._local_raw_dat_dir = self._raw_data_dir if self.mode == "local" \
            else os.path.join("/tmp",
                              str(uuid.uuid1()))

    def _preload_raw_data_file_path(self):
        if self.mode == "distribute":
            if not gfile.Exists(self._local_raw_dat_dir):
                gfile.MakeDirs(self._local_raw_dat_dir)
            os.system("hadoop fs -get {0}/* {1} ".format(self._raw_data_dir, self._local_raw_dat_dir))
        self._all_fpath = [path.join(self._local_raw_dat_dir, f)
                           for f in gfile.ListDirectory(self._local_raw_dat_dir)
                           if not gfile.IsDirectory(path.join(self._local_raw_dat_dir, f))]
        logging.info("all path is :{}".format(self._all_fpath))
        self._all_fpath.sort()

    def _new_raw_data_iter(self):
        raise NotImplementedError("_new_raw_data_iter not implement in base visitor")

    def _load_raw_data_to_mem(self):
        assert self._all_fpath, "raw data file path must not be None"
        for fpath in self._all_fpath:
            raw_data_iter = self._new_raw_data_iter()
            first_item = raw_data_iter.reset_data_iterator(fpath)
            if first_item.example_id != common.InvalidExampleId:
                self.item_dict[first_item.example_id] = first_item
            for item in raw_data_iter:
                if first_item.example_id != common.InvalidExampleId:
                    self.item_dict[item.example_id] = item

        assert self.item_dict, "No raw data in file path"
        self.raw_data_stale = True


class RawDataLoader(RawDataManager):
    def __init__(self, raw_data_dir, raw_data_options, mode):
        super(RawDataLoader, self).__init__(
            raw_data_dir, raw_data_options, mode
        )

    def _new_raw_data_iter(self):
        return DataIterator.build(self._raw_data_options)

