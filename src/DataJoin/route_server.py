import os
import signal
import sys
import time
from concurrent import futures
import traceback

import grpc
from grpc._cython import cygrpc
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from flask import Flask
from DataJoin.routine.data_app import manager as data_app_manager
from DataJoin.routine.parse_data_block_meta_app import manager as parse_data_block_meta_app_manager
from DataJoin.db.db_models import init_db
from DataJoin.utils.api import response_api
from DataJoin.common import common_pb2_grpc
from DataJoin.config import SLEEP_TIME, api_version, HTTP_SERVICE_HOST, HTTP_SERVICE_PORT, \
    PROXY_SERVICE_HOST, PROXY_SERVICE_PORT
from DataJoin.utils.data_transfer import ProxyDataService
from DataJoin.utils.base import get_host_ip
import os


import logging

logging.getLogger().setLevel(logging.INFO)

manager = Flask(__name__)


@manager.errorhandler(500)
def internal_server_error(e):
    logging.error(str(e))
    return response_api(retcode=100, retmsg=str(e))


if __name__ == '__main__':

    manager.url_map.strict_slashes = False
    routine = DispatcherMiddleware(
        manager,
        {
            '/{}/data'.format(api_version): data_app_manager,
            '/{}/parse'.format(api_version): parse_data_block_meta_app_manager,
        }
    )
    http_server_ip = get_host_ip()
    logging.info('http_server_ip is :%s' % http_server_ip)
    mode = os.environ.get("MODE", "local")
    if mode == "distribute":
        init_db()
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         options=[(cygrpc.ChannelArgKey.max_send_message_length, -1),
                                  (cygrpc.ChannelArgKey.max_receive_message_length, -1)])

    common_pb2_grpc.add_ProxyDataServiceServicer_to_server(ProxyDataService(), grpc_server)
    grpc_server.add_insecure_port("{}:{}".format(PROXY_SERVICE_HOST, PROXY_SERVICE_PORT))
    grpc_server.start()
    # start http server
    try:
        run_simple(hostname=HTTP_SERVICE_HOST, port=HTTP_SERVICE_PORT, application=routine, threaded=True)
    except OSError as e:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGKILL)
    except Exception as e:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGKILL)
    try:
        while True:
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        grpc_server.stop(0)
        sys.exit(0)
