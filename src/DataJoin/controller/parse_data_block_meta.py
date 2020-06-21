import sys
import subprocess
import os
from tensorflow.python.platform import gfile
import time
from src.DataJoin.settings import http_server_logger
from src.DataJoin.controller.sync_convert_data_block import StartSyncConvertDataBlock

time_stamp = str(int(time.time()))


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


class DataBlockController(object):
    def __init__(self, dfs_data_block_dir, **kwargs):
        super(DataBlockController).__init__()
        self.dfs_data_block_dir = dfs_data_block_dir

    def data_block_controller(self):
        http_server_logger.info('Fetch Data Block Meta from Path:%s' % self.dfs_data_block_dir)
        data_meta_fpaths = \
            [os.path.join(self.dfs_data_block_dir, f)
             for f in gfile.ListDirectory(self.dfs_data_block_dir)
             if not gfile.IsDirectory(os.path.join(self.dfs_data_block_dir, f))
             and f.endswith(".meta")]
        data_meta_fpaths.sort()
        http_server_logger.info("data_meta_fpaths: %s" % data_meta_fpaths)
        data_block_fpaths = \
            [os.path.join(self.dfs_data_block_dir, f)
             for f in gfile.ListDirectory(self.dfs_data_block_dir)
             if not gfile.IsDirectory(os.path.join(self.dfs_data_block_dir, f))
             and f.endswith(".data")]
        assert len(data_meta_fpaths) == len(data_block_fpaths)
        data_block_fpaths_dict = dict()
        data_meta_fpaths_dict = dict()
        for data_met_path in data_meta_fpaths:
            index = data_met_path.split(".")[-2]
            data_meta_fpaths_dict[str(index)] = data_met_path

        for data_block_path in data_block_fpaths:
            index = data_block_path.split(".")[-3]
            # index = int((data_block_path.split("/")[-1]).split("_")[-1].split(".")[-2])
            data_block_fpaths_dict[str(index)] = data_block_path
        http_server_logger.info("data_block_fpaths:%s" % data_block_fpaths_dict)
        result = list()
        for i in range(len(data_block_fpaths_dict)):
            time.sleep(2)
            meta_path = data_meta_fpaths_dict["{:08}".format(i)]
            data_path = data_block_fpaths_dict["{:08}".format(i)]
            http_server_logger.info("----------meta path-------: %s" % meta_path)
            http_server_logger.info("----------data path--------:%s" % data_path)

            start_sync_data_block_pid = run_subprocess(
                [
                    'python', sys.modules[StartSyncConvertDataBlock.__module__].__file__,
                    '-d', time_stamp,
                    '-m', meta_path,
                    '-p', data_path
                ])


class StartParseDataBlockMeta(object):
    @staticmethod
    def run_task():
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--dfs_data_block_dir', required=False, default='', type=str,
                            help="dfs_data_block_dir")
        parser.add_argument('-mt', '--dfs_data_block_meta', required=False, default='', type=str,
                            help="dfs_data_block_meta")
        parser.add_argument('-db', '--dfs_data_block', required=False, default='', type=str, help="dfs_data_block")
        args = parser.parse_args()
        dfs_data_block_dir = args.dfs_data_block_dir
        if dfs_data_block_dir:
            if dfs_data_block_dir.endswith('/'):
                dfs_data_block_dir = dfs_data_block_dir.strip('/')
            http_server_logger.info('Fetch Data Block Meta from dir:%s' % dfs_data_block_dir)
            dir_fpaths = \
                [os.path.join(dfs_data_block_dir, f)
                 for f in gfile.ListDirectory(dfs_data_block_dir)
                 if gfile.IsDirectory(os.path.join(dfs_data_block_dir, f))]

            # http_server_logger.info(3333333333333333333, dir_fpaths)
            for data_block_path in dir_fpaths:
                DataBlockController(data_block_path).data_block_controller()
        else:
            assert args.dfs_data_block_meta and args.dfs_data_block
            start_sync_data_block_pid = run_subprocess(
                [
                    'python', sys.modules[StartSyncConvertDataBlock.__module__].__file__,
                    '-d', time_stamp,
                    '-m', args.dfs_data_block_meta,
                    '-p', args.dfs_data_block
                ])



if __name__ == '__main__':
    # 解析hdfs上的datablockmeta pb格式化的数据
    StartParseDataBlockMeta().run_task()

