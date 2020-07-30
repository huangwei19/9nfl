from flask import Flask, request

from DataJoin.utils.api import response_api
from DataJoin.controller.parse_data_block_meta import StartParseDataBlockMeta
import sys
import subprocess
import os
import logging

manager = Flask(__name__)


@manager.errorhandler(500)
def internal_server_error(e):
    logging.error(e)
    return response_api(retcode=100, retmsg=str(e))


def run_subprocess(process_cmd):
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
    else:
        startupinfo = None
    p = subprocess.Popen(process_cmd,
                         startupinfo=startupinfo
                         )
    return p


@manager.route('/data/block/meta', methods=['POST'])
def parse_data_block_meta():
    data_block_meta_hdfs_dir = request.json
    dfs_data_block_dir = data_block_meta_hdfs_dir.get('dfs_data_block_dir', '')
    dfs_data_block_meta = data_block_meta_hdfs_dir.get('dfs_data_block_meta', '')
    dfs_data_block = data_block_meta_hdfs_dir.get('dfs_data_block', '')
    if not dfs_data_block_dir and not dfs_data_block_meta and not dfs_data_block:
        return response_api(retcode=999, retmsg='args is null')
    parse_data_block_meta_pid = run_subprocess(
        [
            'python', sys.modules[StartParseDataBlockMeta.__module__].__file__,
            '-d', dfs_data_block_dir,
            '-mt', dfs_data_block_meta,
            '-db', dfs_data_block
        ])
    return response_api(retcode=0, retmsg='success')
