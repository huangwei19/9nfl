# coding: utf-8

import threading
import logging
import traceback
from contextlib import contextmanager
from DataJoin.data_join.data_block_manager import DataBlockMaker, DataBlockManager


class DataBlockSaver(object):
    def __init__(self, partition_id, init_raw_data_loading, data_block_dir, data_source_name):
        self._lock = threading.Lock()
        self._partition_id = partition_id
        self._data_block_manager = \
            DataBlockManager(self._partition_id, data_block_dir, data_source_name)
        self._raw_data_visitor = init_raw_data_loading
        self._next_data_block_index = \
            self._data_block_manager.acquire_produced_data_block_number()
        self._data_block_dir = data_block_dir
        self._data_source_name = data_source_name
        self._data_block_meta_buffer = list()
        self._state_switch = False
        self._send_data_block_meta_finish = False

    def get_next_data_block_index(self):
        with self._lock:
            return self._next_data_block_index

    def append_sent_data_block_meta_to_buffer(self, data_block_meta):
        with self._lock:
            if self._send_data_block_meta_finish:
                raise RuntimeError(
                    "data block saver no need more data block meta"
                )
            if self._next_data_block_index != data_block_meta.data_block_index:
                return False, self._next_data_block_index
            self._data_block_meta_buffer.append(data_block_meta)
            self._next_data_block_index += 1
            return True, self._next_data_block_index

    def finish_sent_data_block_meta(self):
        with self._lock:
            self._send_data_block_meta_finish = True

    def is_need_save(self):
        with self._lock:
            return len(self._data_block_meta_buffer) > 0

    def is_finish_sent_data_block_meta(self):
        with self._lock:
            return self._send_data_block_meta_finish

    @contextmanager
    def build_data_block_saver(self):
        self._sync_with_data_block_manager()
        self._acquire_state_stale()
        yield self._save_data_blocks
        self._release_state_stale()

    def _save_data_blocks(self):
        while self.is_need_save():
            data_block_meta = self._get_next_data_block_meta_from_buffer()
            if data_block_meta is not None:
                self._save_data_block_with_meta(data_block_meta)

    def _acquire_state_stale(self):
        with self._lock:
            self._state_switch = True

    def _release_state_stale(self):
        with self._lock:
            self._state_switch = False

    def _get_next_data_block_meta_from_buffer(self):
        with self._lock:
            if len(self._data_block_meta_buffer) == 0:
                return None
            return self._data_block_meta_buffer[0]

    @contextmanager
    def _build_data_block_maker(self, meta):
        assert self._partition_id == meta.partition_id, \
            "partition id of building data block meta mismatch " \
            "{} != {}".format(self._partition_id, meta.partition_id)
        maker = None
        try:
            maker = \
                DataBlockMaker(self._data_block_dir,
                               self._data_source_name,
                               self._partition_id,
                               meta.data_block_index)
            maker.init_maker_by_input_meta(meta)
            maker.build_data_block_manager(self._data_block_manager)
            yield maker
        except Exception as e:
            logging.error("build data block maker Failed")
            traceback.print_exc(str(e))
        if maker is not None:
            del maker

    def _save_data_block_with_meta(self, meta):
        assert meta is not None, "data block meta need to save should not be None"
        with self._build_data_block_maker(meta) as data_block_maker:
            for example_id in meta.example_ids:
                if example_id in self._raw_data_visitor.item_dict:
                    record = self._raw_data_visitor.item_dict[example_id].record
                    data_block_maker.save_data_record(record)

            saved_data_block_meta = data_block_maker.data_block_finalizer()
            assert saved_data_block_meta == meta, "the saved  data block meta must be " \
                                                  "same with data block meta need to save"
            with self._lock:
                assert self._data_block_meta_buffer[0] == meta
                self._data_block_meta_buffer.pop(0)

    def _is_state_stale(self):
        with self._lock:
            return self._state_switch

    def _sync_with_data_block_manager(self):
        if self._is_state_stale():
            self._remove_saved_data_block_meta_from_buffer()

    def _remove_saved_data_block_meta_from_buffer(self):
        next_data_block_index = \
            self._data_block_manager.acquire_produced_data_block_number()
        with self._lock:
            removed_number = 0
            for meta in self._data_block_meta_buffer:
                if meta.data_block_index >= next_data_block_index:
                    break
                removed_number += 1
            self._data_block_meta_buffer = \
                self._data_block_meta_buffer[removed_number:]
