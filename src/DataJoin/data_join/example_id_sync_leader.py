# coding: utf-8

import threading
import logging
import os
from contextlib import contextmanager

from google.protobuf import empty_pb2

from DataJoin.common import data_join_service_pb2 as dj_pb

from DataJoin.data_join.routine_worker import RoutineWorker
from DataJoin.data_join.data_join_worker import InitRawDataLoading


class ExampleIdSyncLeader(object):

    def __init__(self, peer_client, raw_data_dir, partition_id,
                 rank_id, raw_data_options, mode, init_raw_data_loading_object):
        self._lock = threading.Lock()
        self._peer_client = peer_client
        self._raw_data_dir = raw_data_dir
        self._rank_id = rank_id
        self._mode = mode
        self._raw_data_options = raw_data_options
        self._init_loading = init_raw_data_loading_object
        self._partition_id = partition_id
        self._processor_start = False
        self._processor_routine = dict()

    def start_processors(self):
        with self._lock:
            if not self._processor_start:
                self._processor_routine.update(example_id_sender_processor=RoutineWorker(
                        'example_id_sender_processor',
                        self._send_example_id_processor,
                        self._impl_send_example_id_factor, 6))

                for key, processor in self._processor_routine.items():
                    processor.start_routine()
                self._processor_start = True
                self._enable_example_id_sender_processor()

    def stop_processors(self):
        wait_stop = True
        with self._lock:
            if self._processor_start:
                wait_stop = True
                self._processor_start = False
        if wait_stop:
            for processor in self._processor_routine.values():
                processor.stop_routine()

    def _enable_example_id_sender_processor(self):
        self._processor_routine['example_id_sender_processor'].wakeup()

    def _send_example_id_processor(self, init_loading):
        if not init_loading.follower_finished:
            with self._impl_example_id_sender(init_loading) as sender:
                init_loading.follower_finished = sender()
        if init_loading.partition_finished:
            self._finish_sync_example_id(init_loading)

    def _impl_send_example_id_factor(self):
        with self._lock:
            if self._init_loading is not None:
                self._processor_routine['example_id_sender_processor'].setup_args(
                    self._init_loading
                )
            return self._init_loading is not None

    @contextmanager
    def _impl_example_id_sender(self, init_loading):
        init_loading.acquire_stale_with_sender()

        def sender():
            next_index, follower_finished = \
                self._start_send_example_id(init_loading)
            if follower_finished:
                return True
            examples_list = []
            for (key, example) in init_loading.item_dict.items():
                examples_list.append(example)
                if len(examples_list) > 2048:
                    self._send_example_ids(examples_list, init_loading)
                    examples_list = []
            if len(examples_list) >= 0:
                self._send_example_ids(examples_list, init_loading, True)
            init_loading.partition_finished = True
            return False

        yield sender
        init_loading.release_stale_with_sender()

    def _start_send_example_id(self, init_loading):
        req = dj_pb.StartPartitionRequest(
            rank_id=self._rank_id,
            partition_id=init_loading.partition_id
        )
        rsp = self._peer_client.StartPartition(req)
        if rsp.status.code != 0:
            raise RuntimeError(
                "Failed to call Follower for start to sync id for " \
                "partition {}, reason {}".format(
                    init_loading.partition_id, rsp.status.error_message)
            )
        return rsp.next_index, rsp.finished

    def _send_example_ids(self, examples, init_loading, finished=False):
        send_examples = dj_pb.SyncContent(
            lite_example_ids=dj_pb.LiteExampleIds(
                partition_id=init_loading.partition_id,
                begin_index=0,
                finished=finished
            )
        )
        if len(examples) > 0:
            for exam in examples:
                send_examples.lite_example_ids.example_id.append(exam.example_id)
                send_examples.lite_example_ids.event_time.append(exam.event_time)
        request = dj_pb.SyncPartitionRequest(
            rank_id=self._rank_id,
            partition_id=init_loading.partition_id,
            compressed=False,
            content_bytes=send_examples.SerializeToString()
        )
        response = self._peer_client.SyncPartition(request)
        if response.code != 0:
            raise RuntimeError(
                "Example Id send {} example ids Failed," \
                "error msg {}".format(len(examples), response.error_message)
            )

    def _finish_sync_example_id(self, init_loading):
        if not init_loading.follower_finished:
            logging.info("notified example id sync follower example has been finished")
            request = dj_pb.FinishPartitionRequest(
                rank_id=self._rank_id,
                partition_id=init_loading.partition_id
            )
            response = self._peer_client.FinishPartition(request)
            if response.status.code != 0:
                raise RuntimeError(
                    "visit Follower finish partition Failed" \
                    "error msg: {}".format(response.status.error_message)
                )
            init_loading.follower_finished = response.finished
        if not init_loading.follower_finished:
            logging.info("Follower is still appending example id into queue " \
                          "for partition %d ", init_loading.partition_id)
            return False

        logging.info("Follower has been synced example ids " \
                      "for partition %d", init_loading.partition_id)
        return True

