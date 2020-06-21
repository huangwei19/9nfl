import json

import grpc

from flask import jsonify
from DataJoin.settings import DEFAULT_GRPC_OVERALL_TIMEOUT
from DataJoin.settings import http_server_logger
from DataJoin.utils.grpc_utils import get_grpc_proxy_data_channel, wrap_grpc_proxy_data_packet


def get_json_result(retcode=0, retmsg='success', data=None, job_id=None, meta=None):
    result_dict = {"retcode": retcode, "retmsg": retmsg, "data": data, "jobId": job_id, "meta": meta}
    response = {}
    for key, value in result_dict.items():
        if not value and key != "retcode":
            continue
        else:
            response[key] = value
    return jsonify(response)


def proxy_data_api(method, endpoint, json_body, overall_timeout=DEFAULT_GRPC_OVERALL_TIMEOUT):
    _packet = wrap_grpc_proxy_data_packet(json_body, method, endpoint, overall_timeout=overall_timeout)
    try:
        channel, stub = get_grpc_proxy_data_channel()
        # http_server_logger.info("grpc api request: {}".format(_packet))
        _return = stub.UnaryCall(_packet)
        http_server_logger.info("grpc api response: {}".format(_return))
        channel.close()
        json_body = json.loads(_return.body.value)
        return json_body
    except grpc.RpcError as e:
        raise Exception('rpc request error: {}'.format(e))
    except Exception as e:
        raise Exception('rpc request error: {}'.format(e))


if __name__ == '__main__':
    method = "POST"
    url = "/v1/job/data/block/meta/query"
    json_body = {"block_id": "122222222222222eeee"}
