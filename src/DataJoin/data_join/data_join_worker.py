# coding: utf-8

import logging
import zlib
from concurrent import futures
import tensorflow
import grpc
from google.protobuf import empty_pb2

from DataJoin.common import common_pb2 as common_pb
from DataJoin.common import data_join_service_pb2_grpc as dj_grpc
from DataJoin.common import data_join_service_pb2 as dj_pb
from DataJoin.proxy.channel import make_insecure_channel, ChannelType
from DataJoin.data_join.raw_data_visitor import RawDataLoader

import multiprocessing

from DataJoin.data_join import (
    example_id_sync_leader, example_id_sync_follower,
    example_join_leader, example_join_follower
)
from functools import wraps


class InitRawDataLoading(object):
    def __init__(self, raw_data_dir, raw_data_options, partition_id, mode):
        self.raw_data_loader = RawDataLoader(raw_data_dir,
                                             raw_data_options,
                                             mode
                                             )
        self.partition_finished = False
        self.follower_finished = False
        self.stale_with_sender = True
        self.partition_id = partition_id

    def acquire_stale_with_sender(self):
        self.stale_with_sender = True

    def release_stale_with_sender(self):
        self.stale_with_sender = False

    def __getattr__(self, attribute):
        return getattr(self.raw_data_loader, attribute)


def rank_id_wrap(f):
    @wraps(f)
    def check_rank_id(self, *args, **kwargs):
        assert isinstance(self, DataJoin), \
            "Invalid function type: {}, should be DataJoin".format(type(self))
        assert self._rank_id == args[0].rank_id, \
            "rank_id :{} mismatch peer_rank_id: {} ".format(self._rank_id, args[0].rank_id)
        return f(self, *args, **kwargs)

    return check_rank_id


def partition_id_wrap(f):
    @wraps(f)
    def check_partition_id(self, *args, **kwargs):
        assert isinstance(self, DataJoin), \
            "Invalid function type: {}, should be DataJoin".format(type(self))
        partition_id = args[0].partition_id
        assert partition_id >= 0, \
            "partition id {} should not be negative)".format(partition_id)
        assert self._partition_id == partition_id, \
            "partition_id :{} mismatch peer_partition_id: {} ".format(self._partition_id, partition_id)
        return f(self, *args, **kwargs)

    return check_partition_id


class DataJoin(dj_grpc.DataJoinServiceServicer):
    def __init__(self, peer_client, rank_id, options_args, data_source):
        super(DataJoin, self).__init__()
        self._peer_client = peer_client
        self._rank_id = rank_id
        self._data_source = data_source
        self._role = self._data_source.role
        self._partition_id = self._data_source.partition_id
        self._raw_data_dir = self._data_source.raw_data_dir
        self._data_block_dir = self._data_source.data_block_dir
        self._data_source_name = self._data_source.data_source_name
        self._mode = self._data_source.mode
        self._leader_process = None
        self._follower_process = None
        self._init_raw_data_loading = InitRawDataLoading(self._raw_data_dir, options_args.raw_data_options,
                                                         self._partition_id, self._mode)
        self._init_data_join_processor(options_args)

    def start_data_join_processor(self):
        self._leader_process.start_processors()
        if self._role == common_pb.FLRole.Leader:
            self._follower_process.start_dump_worker()

    def stop_data_join_processor(self):
        self._leader_process.stop_processors()
        self._follower_process.stop_dump_worker()

    @partition_id_wrap
    @rank_id_wrap
    def SyncPartition(self, request, context):
        logging.info("Sync Partition Req:{0}".format(request.partition_id))
        response = common_pb.Status()
        content_bytes = request.content_bytes
        if request.compressed:
            content_bytes = zlib.decompress(content_bytes)
        send_example_items = dj_pb.SyncContent()
        send_example_items.ParseFromString(content_bytes)
        status, _ = self._follower_process.add_example_items(send_example_items)
        if not status:
            response.code = -1
            response.error_message = "not need example items"
        return response

    @partition_id_wrap
    @rank_id_wrap
    def StartPartition(self, request, context):
        logging.info("Start Partition Req:{0}".format(request.partition_id))
        response = dj_pb.StartPartitionResponse()
        peer_partition_id = request.partition_id
        partition_id = \
            self._follower_process.get_partition_id()
        if peer_partition_id != partition_id:
            response.status.code = -2
            response.status.error_message = \
                "partition_id :{0} does not match peer partition_id:{1}".format(partition_id, peer_partition_id)
        if response.status.code == 0:
            response.next_index, response.finished = \
                self._follower_process.start_sync_partition(peer_partition_id)
        return response

    @partition_id_wrap
    @rank_id_wrap
    def FinishPartition(self, request, context):
        logging.info("Finish Partition Req:{0}".format(request.partition_id))
        response = dj_pb.FinishPartitionResponse()
        peer_partition_id = request.partition_id
        partition_id = self._follower_process.get_partition_id()
        assert partition_id == peer_partition_id, \
            "partition_id :{0} does not match peer partition_id:{1}".format(partition_id, peer_partition_id)
        response.finished = \
            self._follower_process.finish_send_partition(
                peer_partition_id
            )
        if response.finished:
            self._follower_process.reset_partition(peer_partition_id)
        return response

    def _init_data_join_processor(self, options_args):
        if self._role == common_pb.FLRole.Leader:
            self._leader_process = \
                example_id_sync_leader.ExampleIdSyncLeader(
                    self._peer_client, self._raw_data_dir, self._partition_id,
                    self._rank_id, options_args.raw_data_options, self._mode, self._init_raw_data_loading
                )
            self._follower_process = \
                example_join_follower.ExampleJoinFollower(
                    self._partition_id, options_args.raw_data_options,
                    self._init_raw_data_loading, self._data_block_dir,
                    self._data_source_name
                )
        else:
            assert self._role == common_pb.FLRole.Follower, \
                "if role not leader, should be Follower"
            follower_data_queue = multiprocessing.Queue(-1)
            self._leader_process = \
                example_join_leader.ExampleJoinLeader(
                    self._peer_client, self._rank_id, self._raw_data_dir,
                    options_args.raw_data_options, options_args.example_joiner_options
                    , self._partition_id, follower_data_queue, self._mode,
                    self._data_block_dir, self._data_source_name
                )
            self._follower_process = \
                example_id_sync_follower.ExampleIdSyncFollower(
                    self._partition_id, follower_data_queue
                )


class DataJoinService(object):
    def __init__(self, peer_address, port, rank_id, options_args, data_source):
        self._data_source_name = data_source.data_source_name
        self._port = port
        self._worker_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        peer_channel = make_insecure_channel(peer_address, ChannelType.REMOTE)
        peer_client = dj_grpc.DataJoinServiceStub(peer_channel)
        self._data_join_worker = DataJoin(
            peer_client, rank_id, options_args, data_source
        )
        dj_grpc.add_DataJoinServiceServicer_to_server(
            self._data_join_worker, self._worker_server
        )
        self._role = "leader" if data_source.role == common_pb.FLRole.Leader else "follower"
        self._worker_server.add_insecure_port('[::]:%d' % port)
        self._data_join_server_started = False

    def start_data_join_service(self):
        if not self._data_join_server_started:
            self._worker_server.start()
            self._data_join_worker.start_data_join_processor()
            self._data_join_server_started = True
            logging.info("Data Join :{0} of data_source :{1} listen on port:{2} ".
                         format(self._role, self._data_source_name, self._port))

    def stop_data_join_service(self):
        if self._data_join_server_started:
            self._data_join_worker.stop_data_join_processor()
            self._worker_server.stop(None)
            self._data_join_server_started = False
            logging.info("Data Join Worker:{0} of data_source :{1} stopped".
                         format(self._role, self._data_source_name))

    def run(self):
        self.start_data_join_service()
        self._worker_server.wait_for_termination()
        self.stop_data_join_service()


class RunDataJoinService(object):
    @staticmethod
    def run_task():
        import argparse
        parser = argparse.ArgumentParser(description='Start DataJoinService ....')
        parser.add_argument('peer_address', type=str,
                            help='uuid or address of peer data join service')
        parser.add_argument('rank_id', type=int,
                            help='the unique id of data join processor')
        parser.add_argument('partition_id', type=int,
                            help='namespace of raw data dir ')
        parser.add_argument('data_source_name', type=str,
                            help='the data source name of data join task')
        parser.add_argument('data_block_dir', type=str,
                            help='data block dir of data join ')
        parser.add_argument('raw_data_dir', type=str,
                            help='the raw data dir of data join')
        parser.add_argument('role', type=str,
                            help='the role of data join')
        parser.add_argument('--mode', '-m', type=str, default='local',
                            help='local or distribute for data join')

        parser.add_argument('--port', '-p', type=int, default=8001,
                            help=' service port of data join  service')

        parser.add_argument('--raw_data_iter', type=str, default='TF_DATASET',
                            help='the type of raw data iter')
        parser.add_argument('--compressed_type', type=str, default='',
                            choices=['', 'ZLIB', 'GZIP'],
                            help='the compressed type of raw data')
        parser.add_argument('--example_joiner', type=str,
                            default='STREAM_JOINER',
                            help='the join method of data joiner')

        parser.add_argument('--dump_data_block_time_span', type=int, default=-1,
                            help='the time span between dump data block and last dump data block')
        parser.add_argument('--dump_data_block_threshold', type=int, default=4096,
                            help='the max count of example items dumped in data block')
        parser.add_argument('--tf_eager_mode', action='store_true',
                            help='use the eager_mode for tf')
        args = parser.parse_args()
        if args.tf_eager_mode:
            tensorflow.compat.v1.enable_eager_execution()
        raw_data_options = dj_pb.RawDataOptions()
        example_joiner_options = dj_pb.ExampleJoinerOptions()
        raw_data_options.raw_data_iter = args.raw_data_iter
        raw_data_options.compressed_type = args.compressed_type
        example_joiner_options.example_joiner = args.example_joiner
        example_joiner_options.dump_data_block_time_span = args.dump_data_block_time_span
        example_joiner_options.dump_data_block_threshold = args.dump_data_block_threshold
        options_args = dj_pb.DataJoinOptions(
            raw_data_options=raw_data_options,
            example_joiner_options=example_joiner_options,
        )
        data_source = common_pb.DataSource()
        data_source.data_source_name = args.data_source_name
        data_source.data_block_dir = args.data_block_dir
        data_source.raw_data_dir = args.raw_data_dir
        data_source.partition_id = args.partition_id
        data_source.mode = args.mode
        if args.role == 'leader':
            data_source.role = common_pb.FLRole.Leader
        else:
            assert args.role == 'follower'
            data_source.role = common_pb.FLRole.Follower
        worker_service = DataJoinService(args.peer_address, args.port,
                                         args.rank_id,
                                         options_args, data_source)
        worker_service.run()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    import logging

    logging.getLogger().setLevel(logging.INFO)
    RunDataJoinService.run_task()

