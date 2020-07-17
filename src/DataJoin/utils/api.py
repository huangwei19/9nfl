import json

import grpc

from flask import jsonify
import logging
from DataJoin.utils.grpc_wrap import get_proxy_data_stub, proxy_data_packet_wrap


def get_result(retcode=0, retmsg='success', data=None, task_id=None):
    result_dict = {"retcode": retcode, "retmsg": retmsg, "data": data, "task_id": task_id}
    response = {}
    for key, value in result_dict.items():
        if not value and key != "retcode":
            continue
        else:
            response[key] = value
    return jsonify(response)


def wrap_proxy_data_api(method, endpoint, json_body):
    packet_wrap = proxy_data_packet_wrap(json_body, method, endpoint)
    try:
        channel, stub = get_proxy_data_stub()
        result_return = stub.UnaryCall(packet_wrap)
        logging.info("grpc api response: {}".format(result_return))
        channel.close()
        json_body = json.loads(result_return.body.value)
        return json_body
    except grpc.RpcError as e:
        raise Exception('rpc request error: {}'.format(e))
    except Exception as e:
        raise Exception('rpc request error: {}'.format(e))


if __name__ == '__main__':
    method = "POST"
    url = "/v1/job/data/block/meta/query"
    json_body = {"block_id": "122222222222222eeee"}
