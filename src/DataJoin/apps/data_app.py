
from flask import Flask, request
import logging
from DataJoin.utils import data_process
from DataJoin.utils.api import get_json_result
from DataJoin.driver.data_controller import DataController

manager = Flask(__name__)


@manager.errorhandler(500)
def internal_server_error(e):
    logging.error(str(e))
    return get_json_result(retcode=100, retmsg=str(e))


@manager.route('/<block_id>/<partition_id>/<file_version>/create/data/block', methods=['POST'])
def create_data_block_meta(block_id, partition_id, file_version):
    DataController.update_data_block_meta_status(block_id=block_id, partition_id=partition_id,
                                                 file_version=int(file_version), data_block_meta_info=request.json,
                                                 create=True)
    return get_json_result(retcode=0, retmsg='success')


@manager.route('/query/data/block/meta', methods=['POST'])
def query_data_block_meta():
    data_block_metas = data_process.query_data_block_meta(**request.json)
    if not data_block_metas:
        return get_json_result(retcode=101, retmsg='find data block meta failed')
    return get_json_result(retcode=0, retmsg='success', data=[task.to_json() for task in data_block_metas])


@manager.route('/query/data/source/meta', methods=['POST'])
def query_data_source_meta():
    data_source_metas = data_process.query_data_source_meta(**request.json)
    if not data_source_metas:
        return get_json_result(retcode=101, retmsg='find data source meta failed')
    return get_json_result(retcode=0, retmsg='success', data=[task.to_json() for task in data_source_metas])


@manager.route('/query/data/source', methods=['POST'])
def query_data_source():
    data_sources = data_process.query_data_source(**request.json)
    if not data_sources:
        return get_json_result(retcode=101, retmsg='find data source failed')
    return get_json_result(retcode=0, retmsg='success', data=[task.to_json() for task in data_sources])
