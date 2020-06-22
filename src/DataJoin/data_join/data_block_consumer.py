# coding: utf-8

import threading

from DataJoin.data_join.processor_manager import ProcessorManager
from DataJoin.data_join.data_block_dumper import DataBlockDumperManager


class DataBlockConsumer(object):
    class DataBlockConsumerWrapper(object):
        def __init__(self, partition_id, init_raw_data_loading,
                     data_block_dir, data_source_name):
            self.data_block_dumper_manager = DataBlockDumperManager(
                partition_id, init_raw_data_loading,
                data_block_dir, data_source_name
            )
            self.partition_id = partition_id

        def __getattr__(self, attr):
            return getattr(self.data_block_dumper_manager, attr)

    def __init__(self, partition_id, raw_data_options, init_raw_data_loading_object,
                 data_block_dir, data_source_name):
        self._lock = threading.Lock()
        self._raw_data_options = raw_data_options
        self._partition_id = partition_id
        self._init_loading = init_raw_data_loading_object
        self._data_block_dir = data_block_dir
        self._data_source_name = data_source_name
        self._processor_routine_map = None
        self.data_block_consumer_wrap = DataBlockConsumer.DataBlockConsumerWrapper(
            partition_id, self._init_loading,
            self._data_block_dir, self._data_source_name
        )
        self._processor_started = False

    def start_sync_partition(self, partition_id):
        with self._lock:
            if self.data_block_consumer_wrap is not None and \
                    self.data_block_consumer_wrap.partition_id != partition_id:
                raise RuntimeError(
                    "partition {} mismatch peer_partition_id:{} ".format(
                        self.data_block_consumer_wrap.partition_id, partition_id)
                )
            next_data_block_index = self.data_block_consumer_wrap.\
                get_next_data_block_index()
            is_meta_finished = self.data_block_consumer_wrap.\
                is_synced_data_block_meta_finished()
            return next_data_block_index, is_meta_finished

    def add_example_items(self, req):
        assert req.HasField('data_block_meta'), \
            "the request must has filed :data_block_meta for DataBlockConsumer"
        with self._lock:
            self._check_status(req.data_block_meta.partition_id)
            return self.data_block_consumer_wrap.add_synced_data_block_meta(
                req.data_block_meta
            )

    def finish_send_partition(self, partition_id):
        with self._lock:
            self._check_status(partition_id)
            self.data_block_consumer_wrap.finish_sync_data_block_meta()
            return not self.data_block_consumer_wrap.need_dump()

    def get_partition_id(self):
        with self._lock:
            return self.data_block_consumer_wrap.partition_id

    def reset_partition(self, partition_id):
        with self._lock:
            if not self._check_status(partition_id):
                return
            if not self.data_block_consumer_wrap.\
                    is_synced_data_block_meta_finished() or \
                    self.data_block_consumer_wrap.need_dump():
                raise RuntimeError("partition {} is consuming "
                                   "data block meta ".format(partition_id))
            self.data_block_consumer_wrap = None

    def start_dump_worker(self):
        with self._lock:
            if not self._processor_started:
                assert self._processor_routine_map is None, \
                    "the data block consumer processor is not None" \
                    " when start processor"
                self._processor_routine_map = ProcessorManager(
                    'data_block_dumper',
                    self._data_block_consumer_processor,
                    self._data_block_consumer_processor_factor, 6
                )
                self._processor_routine_map.active_processor()
                self._processor_started = True

    def stop_dump_worker(self):
        dumper_worker = None
        with self._lock:
            if self._processor_routine_map is not None:
                dumper_worker = self._processor_routine_map
                self._processor_routine_map = None
        if dumper_worker is not None:
            dumper_worker.inactive_processor()

    def _check_status(self, partition_id):
        if partition_id != self.data_block_consumer_wrap.partition_id:
            raise RuntimeError(
                "partition id:{} mismatch peer_partition_id {}".format(
                    partition_id, self.data_block_consumer_wrap.partition_id)
            )
        return True

    def _data_block_consumer_processor(self, data_block_wrap):
        with data_block_wrap.make_data_block_dumper() as dumper:
            dumper()

    def _data_block_consumer_processor_factor(self):
        with self._lock:
            if self.data_block_consumer_wrap is not None \
                    and self.data_block_consumer_wrap.need_dump():
                self._processor_routine_map.build_impl_processor_parameter(self.data_block_consumer_wrap)
                return True
            return False

