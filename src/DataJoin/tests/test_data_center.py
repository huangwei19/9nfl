import grpc
import unittest

from DataJoin.common import data_center_service_pb2
from DataJoin.common import data_center_service_pb2_grpc
import logging


class TestDataCenter(unittest.TestCase):
    def setUp(self):
        self.channel = grpc.insecure_channel('')
        self.client = data_center_service_pb2_grpc.DataBlockQueryServiceStub(self.channel)

    def test_query_data_block(self):
        logging.info('Client QueryDataBlock Start To Request Service')
        data_request = data_center_service_pb2.DataBlockRequest()
        response = self.client.QueryDataBlock(data_request)
        data_block_status = response.data_block_status
        data_block_info = response.data_block_info
        assert data_block_info
        block_id = data_block_info.block_id
        dfs_data_block_dir = data_block_info.dfs_data_block_dir
        error_message = response.error_message
        logging.info("client received data_block_status: %s" % data_block_status)
        logging.info("client received data_block_info: %s" % data_block_info)
        logging.info("client received block_id: %s" % block_id)
        logging.info("client received dfs_data_block_dir: %s" % dfs_data_block_dir)
        logging.info("client received error_message: %s" % error_message)


if __name__ == '__main__':
    unittest.main()
