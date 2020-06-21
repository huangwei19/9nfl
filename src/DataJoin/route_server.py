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
from DataJoin.db.db_models import init_database_tables
from DataJoin.utils.api_utils import get_json_result
from DataJoin.common import proxy_data_pb2_grpc
from DataJoin.settings import _ONE_DAY_IN_SECONDS, API_VERSION, IP, HTTP_PORT, PROXY_DATA_HOST, PROXY_DATA_PORT, http_server_logger
from DataJoin.utils.grpc_utils import ProxyDataService

'''
Initialize the manager
'''
manager = Flask(__name__)


@manager.errorhandler(500)
def internal_server_error(e):
    http_server_logger.exception(e)
    return get_json_result(retcode=100, retmsg=str(e))


if __name__ == '__main__':
    manager.url_map.strict_slashes = False
    app = DispatcherMiddleware(
        manager,
        {
            '/{}/data'.format(API_VERSION): data_app_manager,
            '/{}/parse'.format(API_VERSION): parse_data_block_meta_app_manager,
        }
    )
    data_center_ip = os.environ.get("datacenter_ip")
    http_server_logger.info('data_center_ip is :%s' % data_center_ip)
    # data_center_ip = "10.181.54.64"
    init_database_tables()
    # start grpc server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         options=[(cygrpc.ChannelArgKey.max_send_message_length, -1),
                                  (cygrpc.ChannelArgKey.max_receive_message_length, -1)])

    proxy_data_pb2_grpc.add_ProxyDataServiceServicer_to_server(ProxyDataService(), server)
    server.add_insecure_port("{}:{}".format(PROXY_DATA_HOST, PROXY_DATA_PORT))
    server.start()
    # start http server
    try:
        http_server_logger.info(44444444444444444444444)
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
