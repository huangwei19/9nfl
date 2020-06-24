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
from DataJoin.apps.data_app import manager as data_app_manager
from DataJoin.apps.parse_data_block_meta_app import manager as parse_data_block_meta_app_manager
from DataJoin.db.db_models import init_db
from DataJoin.utils.api import get_json_result
from DataJoin.common import proxy_data_pb2_grpc
from DataJoin.settings import _ONE_DAY_IN_SECONDS, api_version, IP, HTTP_PORT, \
    PROXY_DATA_HOST, PROXY_DATA_PORT
from DataJoin.utils.grpc_wrap import ProxyDataService
from DataJoin.utils.base import get_host_ip
import os


import logging

logging.getLogger().setLevel(logging.INFO)

manager = Flask(__name__)


@manager.errorhandler(500)
def internal_server_error(e):
    logging.error(str(e))
    return get_json_result(retcode=100, retmsg=str(e))


if __name__ == '__main__':

    manager.url_map.strict_slashes = False
    app = DispatcherMiddleware(
        manager,
        {
            '/{}/data'.format(api_version): data_app_manager,
            '/{}/parse'.format(api_version): parse_data_block_meta_app_manager,
        }
    )
    http_server_ip = get_host_ip()
    logging.info('http_server_ip is :%s' % http_server_ip)
    # http_server_ip = "10.181.54.64"
    mode = os.environ.get("MODE", "local")
    if mode == "distribute":
        init_db()
    # start grpc server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         options=[(cygrpc.ChannelArgKey.max_send_message_length, -1),
                                  (cygrpc.ChannelArgKey.max_receive_message_length, -1)])

    proxy_data_pb2_grpc.add_ProxyDataServiceServicer_to_server(ProxyDataService(), server)
    server.add_insecure_port("{}:{}".format(PROXY_DATA_HOST, PROXY_DATA_PORT))
    server.start()
    # start http server
    try:
        logging.info(44444444444444444444444)
        run_simple(hostname=IP, port=HTTP_PORT, application=app, threaded=True)
    except OSError as e:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGKILL)
    except Exception as e:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGKILL)
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
        sys.exit(0)
