import requests
import json
from DataJoin.common import proxy_data_pb2, proxy_data_pb2_grpc
import grpc
from DataJoin.settings import HEADERS, DEFAULT_GRPC_OVERALL_TIMEOUT, \
    http_server_logger
import os
from DataJoin.utils import file_utils


def get_url(_suffix):
    return "http://{0}:{1}/{2}".format('0.0.0.0', 9380, _suffix.lstrip('/'))


def get_grpc_proxy_data_channel():
    channel = grpc.insecure_channel('{}:{}'.format("localhost", "9400"))
    stub = proxy_data_pb2_grpc.ProxyDataServiceStub(channel)
    return channel, stub


def wrap_grpc_proxy_data_packet(_json_body, _method, _url, overall_timeout=DEFAULT_GRPC_OVERALL_TIMEOUT):
    _data = proxy_data_pb2.Data(key=_url, value=bytes(json.dumps(_json_body), 'utf-8'))
    _header = proxy_data_pb2.HeaderData(operator=_method)
    return proxy_data_pb2.Packet(header=_header, body=_data)


class ProxyDataService(proxy_data_pb2_grpc.ProxyDataServiceServicer):
    def UnaryCall(self, _request, context):
        packet = _request
        header = packet.header
        _suffix = packet.body.key
        param_bytes = packet.body.value
        param = bytes.decode(param_bytes)
        method = header.operator
        param_dict = json.loads(param)
        param = bytes.decode(bytes(json.dumps(param_dict), 'utf-8'))

        action = getattr(requests, method.lower(), None)
        http_server_logger.info('rpc receive: {}'.format(packet))
        if action:
            http_server_logger.info("rpc receive:{} {}".format(_suffix, param))
            resp = action(url=get_url(_suffix), data=param, headers=HEADERS)
        else:
            pass
        resp_json = resp.json()
        return wrap_grpc_proxy_data_packet(resp_json, method, _suffix)


def get_grpc_server_directory(server_type):
    return os.path.join(file_utils.get_project_base_directory(), 'servers', server_type)


def get_job_log_directory(server_type):
    return os.path.join(file_utils.get_project_base_directory(), 'logs', server_type)
