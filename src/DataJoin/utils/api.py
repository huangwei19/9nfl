import json
from flask import jsonify
from DataJoin.utils.data_transfer import get_data_transfer_stub, data_transfer_bucket


def response_api(retcode=0, retmsg='success', data=None):
    response_result= {"code": retcode, "msg": retmsg, "data": data}
    return jsonify(response_result)


def wrap_data_transfer_api(request_method, request_url, request_body):
    data_transfer = data_transfer_bucket(request_body, request_method, request_url)
    try:
        data_transfer_channel, data_transfer_stub = get_data_transfer_stub()
        data_transfe_response = data_transfer_stub.UnaryCall(data_transfer)
        data_transfer_channel.close()
        data_transfe_result = json.loads(data_transfe_response.body.value)
        return data_transfe_result
    except Exception as e:
        raise Exception('data transfer error: {}'.format(e))



