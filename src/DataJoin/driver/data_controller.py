
from DataJoin.manager.data_managers import DataManagers


class DataController(object):

    @staticmethod
    def init():
        pass

    @staticmethod
    def update_data_block_meta_status(block_id, partition_id, file_version, data_block_meta_info, create=True):
        data_managers = DataManagers(block_id=block_id, partition_id=partition_id, file_version=file_version)
        data_managers.save_data_block_meta_info(data_block_meta_info=data_block_meta_info, create=create)
