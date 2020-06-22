# coding: utf-8

import threading
import logging
from contextlib import contextmanager
from DataJoin.data_join.data_block_manager import DataBlockMaker, DataBlockManager


class DataBlockDumperManager(object):
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
        self._fly_data_block_meta = []
        self._state_stale = False
        self._synced_data_block_meta_finished = False

    def get_next_data_block_index(self):
        with self._lock:
            return self._next_data_block_index

    def add_synced_data_block_meta(self, meta):
        with self._lock:
            if self._synced_data_block_meta_finished:
                raise RuntimeError(
                    "data block dmuper manager has been mark as " \
                    "no more data block meta"
                )
            if self._next_data_block_index != meta.data_block_index:
                return False, self._next_data_block_index
            self._fly_data_block_meta.append(meta)
            self._next_data_block_index += 1
            return True, self._next_data_block_index

    def finish_sync_data_block_meta(self):
        with self._lock:
            self._synced_data_block_meta_finished = True

    def need_dump(self):
        with self._lock:
            return len(self._fly_data_block_meta) > 0

    def is_synced_data_block_meta_finished(self):
        with self._lock:
            return self._synced_data_block_meta_finished

    @contextmanager
    def make_data_block_dumper(self):
        self._sync_with_data_block_manager()
        self._acquire_state_stale()
        yield self._dump_data_blocks
        self._release_state_stale()

    def _dump_data_blocks(self):
        while self.need_dump():
            meta = self._get_next_data_block_meta()
            if meta is not None:
                self._dump_data_block_by_meta(meta)

    def data_block_meta_sync_finished(self):
        with self._lock:
            return self._synced_data_block_meta_finished

    def _acquire_state_stale(self):
        with self._lock:
            self._state_stale = True

    def _release_state_stale(self):
        with self._lock:
            self._state_stale = False

    def _get_next_data_block_meta(self):
        with self._lock:
            if len(self._fly_data_block_meta) == 0:
                return None
            return self._fly_data_block_meta[0]

    @contextmanager
    def _make_data_block_builder(self, meta):
        assert self._partition_id == meta.partition_id, \
            "partition id of building data block meta mismatch " \
            "{} != {}".format(self._partition_id, meta.partition_id)
        builder = None
        expt = None
        try:
            builder = \
                DataBlockMaker(self._data_block_dir,
                               self._data_source_name,
                               self._partition_id,
                               meta.data_block_index)
            builder.init_by_meta(meta)
            builder.set_data_block_manager(self._data_block_manager)
            yield builder
        except Exception as e:  # pylint: disable=broad-except
            logging.warning("Failed make data block builder, " \
                            "reason %s", e)
            expt = e
        if builder is not None:
            del builder
        if expt is not None:
            raise expt

    def _dump_data_block_by_meta(self, meta):
        assert meta is not None, "input data block must not be None"
        with self._make_data_block_builder(meta) as data_block_builder:
            for example_id in meta.example_ids:
                if example_id in self._raw_data_visitor.item_dict:
                    record = self._raw_data_visitor.item_dict[example_id].record
                    data_block_builder.append_raw_example(record)

            dumped_meta = data_block_builder.finish_data_block()
            assert dumped_meta == meta, "the generated dumped meta shoud " \
                                        "be the same with input mata"
            with self._lock:
                assert self._fly_data_block_meta[0] == meta
                self._fly_data_block_meta.pop(0)

    def _is_state_stale(self):
        with self._lock:
            return self._state_stale

    def _sync_with_data_block_manager(self):
        if self._is_state_stale():
            self._evict_dumped_data_block_meta()

    def _evict_dumped_data_block_meta(self):
        next_data_block_index = \
            self._data_block_manager.acquire_produced_data_block_number()
        with self._lock:
            skip_count = 0
            for meta in self._fly_data_block_meta:
                if meta.data_block_index >= next_data_block_index:
                    break
                skip_count += 1
            self._fly_data_block_meta = \
                self._fly_data_block_meta[skip_count:]
