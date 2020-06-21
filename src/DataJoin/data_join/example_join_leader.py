# coding: utf-8

import threading
import logging
import zlib
from contextlib import contextmanager

from google.protobuf import empty_pb2

from src.DataJoin.common import data_join_service_pb2 as dj_pb

from src.DataJoin.data_join.routine_worker import RoutineWorker
from src.DataJoin.data_join.joiner_impl.example_joiner import DataJoiner
from src.DataJoin.data_join.joiner_impl.stream_joiner import MemoryDataJoiner


class ExampleJoinLeader(object):
    class DataJoinerWrapper(object):
        def __init__(self,
                     example_joiner_options, raw_data_options, data_block_dir,
                     data_source_name, raw_data_dir, partition_id, mode, queue):
            self.data_joiner = DataJoiner.build_data_joiner(example_joiner_options,
                                                            raw_data_options,
                                                            data_block_dir,
                                                            data_source_name,
                                                            raw_data_dir,
                                                            partition_id,
                                                            mode, queue)
            self.next_data_block_index = 0
            self.data_block_producer_finished = False

        def get_next_data_block_meta(self):
            assert self.next_data_block_index >= 0
            return self.data_joiner.get_data_block_meta_by_index(
                self.next_data_block_index
            )

        def __getattr__(self, attribute):
            return getattr(self.data_joiner, attribute)

    def __init__(self, peer_client, rank_id, raw_data_dir,
                 raw_data_options, example_joiner_options,
                 partition_id, queue, mode, data_block_dir,
                 data_source_name):
        self._lock = threading.Lock()
        self._peer_client = peer_client
        self._raw_data_dir = raw_data_dir
        self._rank_id = rank_id
        self._partition_id = partition_id
        self._mode = mode
        self._data_block_dir = data_block_dir
        self._data_source_name = data_source_name
        self._raw_data_options = raw_data_options
        self._example_joiner_options = example_joiner_options
        self._queue = queue
        self._data_join_wrap = None
        self._processor_start = False
        self._processor_routine = dict()

    def start_processors(self):
        with self._lock:
            if not self._processor_start:
                self._processor_routine.update(
                    build_data_joiner=RoutineWorker(
                        'build_data_joiner',
                        self._build_data_joiner_processor,
                        self._impl_build_data_joiner_factor, 6),
                    data_joiner=RoutineWorker(
                        'data_joiner',
                        self._data_join_processor,
                        self._impl_data_join_factor, 5),
                    data_block_meta_sender=RoutineWorker(
                        'data_block_meta_sender',
                        self._send_data_block_meta_processor,
                        self._impl_send_data_block_meta_factor, 5)
                )

                for processor in self._processor_routine.values():
                    processor.start_routine()
                self._processor_start = True

    def stop_processors(self):
        wait_stop = True
        with self._lock:
            if self._processor_start:
                wait_stop = True
                self._processor_start = False
        if wait_stop:
            for processor in self._processor_routine.values():
                processor.stop_routine()

    def _enable_build_data_joiner_processor(self):
        self._data_join_wrap = None
        self._processor_routine.get('build_data_joiner').wakeup()

    def _build_data_joiner_processor(self):
        data_join_wrap = ExampleJoinLeader.DataJoinerWrapper(
            self._example_joiner_options, self._raw_data_options,
            self._data_block_dir,
            self._data_source_name, self._raw_data_dir,
            self._partition_id, self._mode, self._queue
        )
        with self._lock:
            assert self._data_join_wrap is None
            self._data_join_wrap = data_join_wrap
            self._enable_data_join_processor()
            self._enable_data_block_meta_sender()

    def _impl_build_data_joiner_factor(self):
        with self._lock:
            return self._data_join_wrap is None

    def _enable_data_join_processor(self):
        self._processor_routine.get('data_joiner').wakeup()

    def _data_join_processor(self, data_join_wrap):
        assert isinstance(data_join_wrap, ExampleJoinLeader.DataJoinerWrapper)
        if data_join_wrap.data_join_switch():
            with data_join_wrap.data_joiner_factory() as joiner:
                for data_block_meta in joiner:
                    if data_block_meta is None:
                        continue
                    self._enable_data_block_meta_sender()

    def _impl_data_join_factor(self):
        with self._lock:
            if self._data_join_wrap is not None:
                self._processor_routine.get('data_joiner').setup_args(self._data_join_wrap)
            return self._data_join_wrap is not None

    def _enable_data_block_meta_sender(self):
        self._processor_routine.get('data_block_meta_sender').wakeup()

    def _send_data_block_meta_processor(self, data_join_wrap):
        assert isinstance(data_join_wrap, ExampleJoinLeader.DataJoinerWrapper)
        joined_finished = False
        if not data_join_wrap.data_block_producer_finished:
            with self._send_data_block_meta_executor(data_join_wrap) as send_executor:
                joined_finished = send_executor()
        if joined_finished or data_join_wrap.data_block_producer_finished:
            self._finish_send_data_block_meta(data_join_wrap)

    def _impl_send_data_block_meta_factor(self):
        with self._lock:
            if self._data_join_wrap is not None:
                self._processor_routine.get('data_block_meta_sender').setup_args(
                    self._data_join_wrap
                )
            return self._data_join_wrap is not None

    @contextmanager
    def _send_data_block_meta_executor(self, data_join_wrap):
        assert isinstance(data_join_wrap, ExampleJoinLeader.DataJoinerWrapper)

        def send_executor():
            data_join_wrap.next_data_block_index, data_join_wrap.data_block_producer_finished = \
                self._sync_data_block_meta_sender_status(data_join_wrap)
            join_finished = False
            while not data_join_wrap.data_block_producer_finished:
                print("***********Next Data Block Index*******", data_join_wrap.next_data_block_index)
                join_finished, meta = data_join_wrap.get_next_data_block_meta()
                if meta is None:
                    break
                print("------------Send Data Block Meta-----------", meta.block_id)
                self._send_data_block_meta(meta)
                data_join_wrap.next_data_block_index += 1
            return join_finished

        yield send_executor

    def _sync_data_block_meta_sender_status(self, data_join_wrap):
        assert isinstance(data_join_wrap, ExampleJoinLeader.DataJoinerWrapper)
        req = dj_pb.StartPartitionRequest(
            rank_id=self._rank_id,
            partition_id=data_join_wrap._partition_id
        )
        rsp = self._peer_client.StartPartition(req)
        if rsp.status.code != 0:
            raise RuntimeError(
                "Failed to call data block consumer for syncing data block meta sender status "
                "for partition_id {}, error msg {}".format(data_join_wrap._partition_id, rsp.status.error_message)
            )
        return rsp.next_index, rsp.finished

    def _send_data_block_meta(self, meta):
        str_data_block_meta = dj_pb.SyncContent(data_block_meta=meta).SerializeToString()
        request = dj_pb.SyncPartitionRequest(
            rank_id=self._rank_id,
            content_bytes=str_data_block_meta,
            compressed=False
        )
        if len(str_data_block_meta) > (2 << 20):
            compressed_data_block_meta = zlib.compress(str_data_block_meta, 5)
            if len(compressed_data_block_meta) < len(str_data_block_meta) * 0.8:
                request.content_bytes = compressed_data_block_meta
                request.compressed = True
        rsp = self._peer_client.SyncPartition(request)
        if rsp.code != 0:
            raise RuntimeError(
                "data block producer call data block consumer for sending"
                " data block meta Failed {} data_block_index: {}," \
                "error msg {}".format(meta.block_id, meta.data_block_index, rsp.error_message)
            )

    def _finish_send_data_block_meta(self, data_join_wrap):
        assert isinstance(data_join_wrap, ExampleJoinLeader.DataJoinerWrapper)
        assert data_join_wrap.is_data_joiner_finished()
        if not data_join_wrap.data_block_producer_finished:
            request = dj_pb.FinishPartitionRequest(
                rank_id=self._rank_id,
                partition_id=data_join_wrap._partition_id
            )
            response = self._peer_client.FinishPartition(request)
            if response.status.code != 0:
                raise RuntimeError(
                    "Data block producer call Data block consumer for finishing partition Failed " \
                    "error msg : {}".format(response.status.error_message)
                )
            data_join_wrap.data_block_producer_finished = response.finished

        if not data_join_wrap.data_block_producer_finished:
            logging.info("Need to wait reason: data block is still producing for " \
                         "partition %d ", data_join_wrap._partition_id)
            return False
        logging.info("data block producing has been finished " \
                     "for partition %d", data_join_wrap._partition_id)
        return True
