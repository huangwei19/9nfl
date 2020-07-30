import requests
import json
from DataJoin.common import common_pb2, common_pb2_grpc
import grpc
import logging
from DataJoin.config import HEADERS,PROXY_SERVICE_PORT,\
    PROXY_SERVICE_HOST,HTTP_SERVICE_HOST,HTTP_SERVICE_PORT


def get_data_transfer_stub():
    proxy_channel = grpc.insecure_channel('{}:{}'.format(str(PROXY_SERVICE_HOST), str(PROXY_SERVICE_PORT)))
    data_stub = common_pb2_grpc.ProxyDataServiceStub(proxy_channel)
    return proxy_channel, data_stub


def data_transfer_bucket(json_result, request_method, request_url):
    data_result = common_pb2.Data(key=request_url, value=bytes(json.dumps(json_result), 'utf-8'))
    data_header = common_pb2.HeaderData(operator=request_method)
    return common_pb2.Packet(header=data_header, body=data_result)


class ProxyDataService(common_pb2_grpc.ProxyDataServiceServicer):
    def UnaryCall(self, _request, context):
        request_header = _request.header
        request_url = _request.body.key
        request_args = bytes.decode(_request.body.value)
        request_method = request_header.operator
        request_args = json.loads(request_args)
        request_args = bytes.decode(bytes(json.dumps(request_args), 'utf-8'))

        request_executor = getattr(requests, request_method.lower(), None)
        if request_executor:
            logging.info("rpc service receive request url:{},request args: {}".format(request_url, request_args))
            url = "http://{0}:{1}/{2}".format(str(HTTP_SERVICE_HOST), HTTP_SERVICE_PORT, request_url.lstrip('/'))
            response_result = request_executor(url=url, data=request_args, headers=HEADERS)
        else:
            pass
        response_json_result = response_result.json()
        return data_transfer_bucket(response_json_result, request_method, request_url)
