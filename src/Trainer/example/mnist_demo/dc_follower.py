#-*- encoding=utf-8-*-
# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the gRPC route guide server."""

from concurrent import futures
import time
import math
import logging
import sys
import subprocess

sys.path.insert(0, '../fl_pkgs/')
sys.path.insert(0, '../')
sys.path.insert(0, './fl_pkgs/')
sys.path.insert(0, './')

try:
    import queue
except ImportError:
    import Queue as queue

import grpc

from fl_comm_libs.proto import dc_agent_pb2
from fl_comm_libs.proto import dc_agent_pb2_grpc


logging.basicConfig(level = logging.INFO, \
    format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', \
    stream = sys.stdout, \
    datefmt = '%a, %d %b %Y %H:%M:%S', \
    filemode = 'a')


def run(cmd):
    """
    获取shell的结果
    """
    logging.info(cmd)
    buff = subprocess.check_output(cmd, shell=True)
    return str(buff, encoding='utf-8')


class DcLeaderServer(dc_agent_pb2_grpc.DataBlockQueryServiceServicer):

    def __init__(self, hdfs_dir):
        self.hdfs_dir = hdfs_dir
        self._load_data()

    def _load_data(self):
        """
        follower用dict
        """
        file_list = run("hadoop fs -ls %s 2>/dev/null|awk '{print $NF}'|grep -E -v 'items'" 
           % self.hdfs_dir).split('\n')
        self._db_dict = {}
        for fpath in file_list:
            request_id = fpath.split('/')[-1]
            self._db_dict[request_id] = (request_id, fpath)
    
    def QueryDataBlock(self, request, context):
        """
        follower需要读request_id
        """
        datablock = dc_agent_pb2.FetchDataBlockResponse()
        db = self._db_dict.get(request.request_id)
        if db:
            datablock.status_code = dc_agent_pb2.OK
            datablock.db_info.request_id = db[0]
            datablock.db_info.data_path = db[1]
        else:
            datablock.status_code = dc_agent_pb2.ERROR_ABORTED
        logging.info("status_code: %s, request_id: %s" % (datablock.status_code,
            datablock.db_info.request_id))
        return datablock


def serve(hdfs_path):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    dc_agent_pb2_grpc.add_DataBlockQueryServiceServicer_to_server(
        DcLeaderServer(hdfs_path), server)
    server.add_insecure_port('[::]:40005')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python %s hdfs_path" % sys.argv[0])
        sys.exit(-1)
    #hdfs_path = '/user/jd_ad/ads_conv/fl_jingtiao/demo/mnist/leader_train'
    hdfs_path = sys.argv[1]
    print("Server start loadding %s" % hdfs_path)
    serve(hdfs_path)
