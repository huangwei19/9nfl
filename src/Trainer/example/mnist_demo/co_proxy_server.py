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

sys.path.insert(0, '../fl_pkgs/')
sys.path.insert(0, '../')
sys.path.insert(0, './fl_pkgs/')
sys.path.insert(0, './')

import grpc

from fl_comm_libs.proto import co_proxy_pb2 as co_pb
from fl_comm_libs.proto import co_proxy_pb2_grpc as co_grpc

worker_pairs = {}

class CoProxyServicer(co_grpc.PairServiceServicer):

    def __init__(self):
        pass

    def RegisterUUID(self, request, context):
        for uuid in request.uuid:
          if uuid in worker_pairs:
            if (request.ip_port not in worker_pairs[uuid]):
              worker_pairs[uuid].add(request.ip_port)
            else:
              print('Skip register ' + request.ip_port)
          else:
            worker_pairs[uuid] = {request.ip_port}
        print(worker_pairs)
        s = co_pb.Status()
        s.status = 0
        return s
    
    def GetPairInfo(self, request, context):
        print('Process GetPairInfo')
        resp = co_pb.PairInfoResponse()
        for uuid in request.uuid:
          if uuid in worker_pairs:
            if len(worker_pairs[uuid]) >= 2:
              serv = resp.service_map.add()
              serv.local_uuid = uuid
              serv.remote_uuid = uuid
              resp.status.status = 0
              resp.status.err_msg = 'OK'
            else:
              print('No pair for ' + uuid)
              resp.status.status = 1
              resp.status.err_msg = 'Worker Pair not ready.'
              break
          else:
            resp.status.status = 1
            resp.status.err_msg = 'Worker Pair not ready.'
            print('No Register workers...')
            break
        print('Stored workers pairs:')
        print(worker_pairs)
        print('Responce:')
        print(resp)
        return resp


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    co_grpc.add_PairServiceServicer_to_server(
        CoProxyServicer(), server)
    server.add_insecure_port('[::]:40004')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    print("CoProxy Test Server start...")
    serve()
