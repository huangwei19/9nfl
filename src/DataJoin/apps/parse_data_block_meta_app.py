
from flask import Flask, request

from src.DataJoin.settings import http_server_logger
from src.DataJoin.utils.api_utils import get_json_result
from src.DataJoin.controller.parse_data_block_meta import StartParseDataBlockMeta
from src.DataJoin.utils import core
import sys
from src.DataJoin.utils.grpc_utils import get_grpc_server_directory, get_job_log_directory

manager = Flask(__name__)


@manager.errorhandler(500)
def internal_server_error(e):
    http_server_logger.exception(e)
    return get_json_result(retcode=100, retmsg=str(e))


@manager.route('/data/block/meta', methods=['POST'])
def parse_data_block_meta():
    data_block_meta_hdfs_dir = request.json
    dfs_data_block_dir = data_block_meta_hdfs_dir.get('dfs_data_block_dir', '')
    dfs_data_block_meta = data_block_meta_hdfs_dir.get('dfs_data_block_meta', '')
    dfs_data_block = data_block_meta_hdfs_dir.get('dfs_data_block', '')
    if not dfs_data_block_dir and not dfs_data_block_meta and not dfs_data_block:
        return get_json_result(retcode=999, retmsg='args is null')
    parse_data_block_meta_pid = core.run_subprocess(
        get_grpc_server_directory("parse_data_block_meta"),
        [
            'python', sys.modules[StartParseDataBlockMeta.__module__].__file__,
            '-d', dfs_data_block_dir,
            '-mt', dfs_data_block_meta,
            '-db', dfs_data_block
        ],
        get_job_log_directory("parse_data_block_meta"))
    return get_json_result(retcode=0, retmsg='success')

