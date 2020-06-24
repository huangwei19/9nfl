import grpc
from DataJoin.common import data_center_service_pb2
from DataJoin.common import data_center_service_pb2_grpc
from concurrent import futures
import time
import json
from DataJoin.utils.api import proxy_data_api
import logging
import os
from DataJoin.data_center.counter import Counter
from DataJoin.data_center.data_block_manager import DataBlockMetaManage, ReidsHandle
import traceback
import sys
from DataJoin.settings import api_version, DATA_CENTER_PORT
import queue
from tensorflow.compat.v1 import gfile
from os import path
from DataJoin.utils.base import get_host_ip

'''
train_data_start = time_str_to_timestamp(str(os.environ.get("train_data_start", '')))
train_data_end = time_str_to_timestamp(str(os.environ.get("train_data_end", '')))
train_data_start = 150003072
train_data_end = 150005119
'''
train_data_start = int(
    str(os.environ.get("train_data_start", 300000000)).replace("-", "").replace(":", "").replace(" ", ""))
train_data_end = int(str(os.environ.get("train_data_end", 30000000)).replace("-", "").replace(":", "").replace(" ", ""))
data_num_epoch = os.environ.get("data_num_epoch", 1)
data_source_name = os.environ.get("data_source_name", "jd_bd_dsp_data_source")


class DataBlockMeta(object):
    def __init__(self, **kwargs):
        super(DataBlockMeta, self).__init__()
        self.block_id = kwargs.get("block_id", "")
        self.partition_id = kwargs.get("partition_id", 0)
        self.file_version = kwargs.get("file_version", 0)
        self.start_time = kwargs.get("start_time", 0)
        self.end_time = kwargs.get("end_time", 0)
        self.example_ids = [v.encode("utf-8") for v in json.loads(kwargs.get("example_ids", []))] if kwargs.get(
            "example_ids", []) else []
        self.leader_start_index = kwargs.get("leader_start_index", 0)
        self.leader_end_index = kwargs.get("leader_end_index", 0)
        self.follower_restart_index = kwargs.get("follower_restart_index", 0)
        self.data_block_index = kwargs.get("data_block_index", 0)

    def create_data_block_meta(self):
        data_block_meta = data_center_service_pb2.DataBlockMeta()
        data_block_meta.block_id = self.block_id
        data_block_meta.partition_id = self.partition_id
        data_block_meta.file_version = self.file_version
        data_block_meta.start_time = self.start_time
        data_block_meta.end_time = self.end_time
        data_block_meta.leader_start_index = self.leader_start_index
        data_block_meta.leader_end_index = self.leader_end_index
        data_block_meta.follower_restart_index = self.follower_restart_index
        data_block_meta.data_block_index = self.data_block_index
        data_block_meta.example_ids.extend(self.example_ids)
        return data_block_meta


class DataBlockQueryService(data_center_service_pb2_grpc.DataBlockQueryServiceServicer):
    def __init__(self, data_center_mode: str = None, data_bloc_dir: str = None):
        self.data_center_mode = data_center_mode
        if self.data_center_mode == "local":
            self._data_center_queue = queue.Queue()
            self.data_bloc_dir = data_bloc_dir
            self._block_id_map = dict()
            self.file_path_list = list()
            assert self.data_bloc_dir is not None, \
                "data_bloc_dir should not be None if mode is local"
            self.dir_path_list = [path.join(self.data_bloc_dir, f)
                                  for f in gfile.ListDirectory(self.data_bloc_dir)
                                  if gfile.IsDirectory(path.join(self.data_bloc_dir, f))]
            for dir_path in self.dir_path_list:
                self.file_path_list += [path.join(dir_path, f)
                                        for f in gfile.ListDirectory(dir_path)
                                        if f.split(".")[-1] == "data" and
                                        not gfile.IsDirectory(path.join(dir_path, f))]
            self.file_path_list.sort()
            self.encode_leader_data_block_info()
            self.encode_follower_data_block_info()

    def encode_leader_data_block_info(self):
        for i in range(data_num_epoch):
            for file_path in self.file_path_list:
                block_id = (file_path.split('/')[-1]).replace(".data", "")
                self._data_center_queue.put((block_id, file_path))
                logging.info("block_id:{}, data_block_path: {}".format(block_id, file_path))

    def encode_follower_data_block_info(self):
        for file_path in self.file_path_list:
            block_id = (file_path.split('/')[-1]).replace(".data", "")
            self._block_id_map[block_id] = file_path

    def QueryDataBlock(self, request, context):
        logging.info('server received :%s from client QueryDataBlock ' % request)
        data_block_dict = None
        block_id = request.block_id
        endpoint = "/{0}/data/query/data/block/meta".format(api_version)
        # parse received data from client request
        try:

            if not block_id:
                if self.data_center_mode == "local":
                    if not self._data_center_queue.empty():
                        data_block_queue = self._data_center_queue.get()
                        data_block_info = data_center_service_pb2.DataBlockInfo(
                            block_id=data_block_queue[0],
                            dfs_data_block_dir=data_block_queue[1])
                        data_response = data_center_service_pb2.DataBlockResponse(
                            data_block_status=data_center_service_pb2.DataBlockStatus.Value("OK"),
                            error_message="trainer request server query block success",
                            data_block_info=data_block_info)
                        return data_response
                    else:
                        return data_center_service_pb2.DataBlockResponse(
                            data_block_status=data_center_service_pb2.DataBlockStatus.Value("FINISHED"),
                            error_message="trainer request server query block finished")

                json_body = {}
                if train_data_start and train_data_end:
                    json_body["start_time"] = train_data_start
                    json_body["end_time"] = train_data_end
                if data_source_name:
                    json_body["data_source_name"] = data_source_name
                t = Counter()
                num = t.run()
                logging.info('execute query data block meta current num :%s' % num)
                logging.info('data num epoch :%s' % data_num_epoch)
                redis_handle = ReidsHandle()
                if num == 1:
                    logging.info('server received json_body :%s from client QueryDataBlock ' % json_body)
                    data_block_result = proxy_data_api("POST", endpoint, json_body)
                    data_block_check_null_status = DataBlockMetaManage().check_result_null(**data_block_result)
                    if data_block_check_null_status:
                        return data_block_check_null_status
                    data_block_result = data_block_result.get("data", [])
                    data_block_dict = data_block_result[0]
                    data_length = len(data_block_result)
                    total_epoch_time = data_length * int(data_num_epoch)
                    data_block_redis = dict(data_block_result=data_block_result, total_epoch_time=total_epoch_time)

                    redis_handle.redis_set(json.dumps(data_block_redis))
                else:
                    status, data_block_redis = redis_handle.redis_get()
                    if not status:
                        data_block_meta_status = DataBlockMetaManage(2, 1).check_result_null(**{})
                        if data_block_meta_status:
                            return data_block_meta_status
                    data_block_result = (json.loads(data_block_redis)).get("data_block_result", [])
                    total_epoch_time = (json.loads(data_block_redis)).get("total_epoch_time", 0)
                    data_length = total_epoch_time / int(data_num_epoch)
                    if num < total_epoch_time:
                        if num % data_length == 0:
                            data_block_dict = data_block_result[-1]
                        else:
                            logging.info('current data block meta index :%s ' % (int(num % data_length - 1)))
                            data_block_dict = data_block_result[int(num % data_length - 1)]
                    elif num == total_epoch_time:
                        data_block_dict = data_block_result[-1]
                        redis_handle.redis_delete()
                    data_block_check_ready_status = DataBlockMetaManage(num, total_epoch_time).check_result_status(
                        **data_block_dict)
                    if data_block_check_ready_status:
                        return data_block_check_ready_status

            else:
                if self.data_center_mode == "local":
                    if self._block_id_map.get(block_id, None):
                        data_block_info = data_center_service_pb2.DataBlockInfo(
                            block_id=block_id,
                            dfs_data_block_dir=self._block_id_map[block_id])
                        data_response = data_center_service_pb2.DataBlockResponse(
                            data_block_status=data_center_service_pb2.DataBlockStatus.Value("OK"),
                            error_message="trainer request server query block success",
                            data_block_info=data_block_info)
                    else:
                        data_response = data_center_service_pb2.DataBlockResponse(
                            data_block_status=data_center_service_pb2.DataBlockStatus.Value("NOT_FOUND"),
                            error_message="Not Found Data Block")
                    return data_response
                json_body = {"block_id": block_id}
                logging.info('server received json_body :%s from client QueryDataBlock ' % json_body)
                data_block_result = proxy_data_api("POST", endpoint, json_body)
                data_block_check_null_status = DataBlockMetaManage().check_result_null(**data_block_result)
                if data_block_check_null_status:
                    return data_block_check_null_status
                data_block_result = data_block_result.get("data", [])
                data_block_dict = data_block_result[0]
                data_block_check_ready_status = DataBlockMetaManage().check_result_status(**data_block_dict)
                if data_block_check_ready_status:
                    return data_block_check_ready_status

            data_block_obj = DataBlockMeta(**data_block_dict)
            data_block_meta = data_block_obj.create_data_block_meta()
            data_block_info = data_center_service_pb2.DataBlockInfo(block_id=data_block_dict.get("block_id", ""),
                                                                    dfs_data_block_dir=data_block_dict.get(
                                                                        "dfs_data_block_dir", ""),
                                                                    data_block_meta=data_block_meta)
            data_response = data_center_service_pb2.DataBlockResponse(
                data_block_status=data_center_service_pb2.DataBlockStatus.Value("OK"),
                error_message="trainer request server query block success",
                data_block_info=data_block_info)

            return data_response
        except Exception as e:
            logging.info('query data block meta exec :%s' % str(e))
            traceback.print_exc(file=sys.stdout)
            return data_center_service_pb2.DataBlockResponse(
                data_block_status=data_center_service_pb2.DataBlockStatus.Value("ABORTED"),
                error_message="query data block aborted")


class StartDataCenterServer(object):
    @staticmethod
    def run_server():
        # 启动 rpc 服务
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('--mode', '-m', type=str, default='local',
                            help='local or distribute for data center service')
        parser.add_argument('--data_block_dir', type=str, default='',
                            help='data block dir is need if mode is local for data center service')
        args = parser.parse_args()
        data_center_host = get_host_ip()
        data_center_port = DATA_CENTER_PORT
        data_center_mode = args.mode
        data_block_dir = args.data_block_dir
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        data_center_service_pb2_grpc.add_DataBlockQueryServiceServicer_to_server(
            DataBlockQueryService(data_center_mode, data_block_dir), server)
        server.add_insecure_port('{}:{}'.format(data_center_host, data_center_port))
        server.start()
        logging.info("start data center server successfully host:{},port:{}".format(data_center_host, data_center_port))
        try:
            while True:
                time.sleep(60 * 60 * 24)
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == '__main__':
    StartDataCenterServer.run_server()
