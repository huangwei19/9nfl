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

sys.path.insert(0, '../fl_pkgs')
sys.path.insert(0, '../')
sys.path.insert(0, './fl_pkgs')
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

    def __init__(self, hdfs_dir, n_epoch=1):
        self.hdfs_dir = hdfs_dir
        self.n_epoch = n_epoch
        self._load_data()

    def _load_data(self):
        """
        leader用queue
        """
        file_list = run("hadoop fs -ls %s 2>/dev/null|awk '{print $NF}'|grep -E -v 'items'" 
           % self.hdfs_dir).split('\n')
        self._db_queue = queue.Queue()
        for i in range(self.n_epoch):
            for fpath in file_list:
                request_id = fpath.split('/')[-1]
                if "tfrecord" in request_id:
                    self._db_queue.put((request_id, fpath))
    
    def QueryDataBlock(self, request, context):
        """
        leader不读request, 直接从queue里取一个
        """
        datablock = dc_agent_pb2.FetchDataBlockResponse()
        if not self._db_queue.empty():
            db = self._db_queue.get(block=True, timeout=5)
            if db:
                datablock.status_code = dc_agent_pb2.OK
                datablock.db_info.request_id = db[0]
                datablock.db_info.data_path = db[1]
            else:
                datablock.status_code = dc_agent_pb2.ERROR_ABORTED
        else:
            datablock.status_code = dc_agent_pb2.FINISHED
        logging.info("status_code: %s, request_id: %s" % (datablock.status_code,
            datablock.db_info.request_id))
        return datablock


def serve(hdfs_path, n_epoch):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    dc_agent_pb2_grpc.add_DataBlockQueryServiceServicer_to_server(
        DcLeaderServer(hdfs_path, n_epoch), server)
    server.add_insecure_port('[::]:40003')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python %s hdfs_path" % sys.argv[0])
        sys.exit(-1)
    #hdfs_path = '/user/jd_ad/ads_conv/fl_jingtiao/demo/mnist/leader_train'
    hdfs_path = sys.argv[1]
    n_epoch = 3
    print("Server start loadding %s" % hdfs_path)
    serve(hdfs_path, n_epoch)
