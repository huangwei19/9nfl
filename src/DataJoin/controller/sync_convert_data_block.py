import tensorflow as tf
import os
from DataJoin.common import data_join_service_pb2
from google.protobuf import text_format
import logging
from DataJoin.utils.api import wrap_data_transfer_api
from DataJoin.utils.base import get_host_ip

EXAMPLE_ID = "example_id"
EVENT_TIME = "event_time"
LABEL = "label"
EXAMPLE_ID_NS = '%X'
DEFATLT_LABEL = "0 0"
import codecs

http_server_ip = get_host_ip()
data_path_vw_bas_dir = os.environ.get("data_path_vw_bas_dir", None)


def map_fn(proto):
    example = tf.train.Example.FromString(proto)
    f_dict = {}
    feature_map = example.features.feature
    for feat in feature_map:
        if feat == EVENT_TIME:
            continue
        elif feat == EXAMPLE_ID:
            f_dict[EXAMPLE_ID_NS] = feature_map[feat].bytes_list.value
        else:
            f_dict[feat] = feature_map[feat].bytes_list.value
    if LABEL in f_dict:
        label = str(f_dict.pop(LABEL)[0], encoding='utf-8')
    else:
        label = DEFATLT_LABEL
    res = [label, ]
    for ns in f_dict:
        for val in f_dict[ns]:
            try:
                val = str(val, encoding='utf-8')
            except Exception as e:
                ns = ns.encode('utf-8')
            res.append("%s %s" % (ns, val))
    return "|".join(res)


def write_data(input_file, output_file, batch_size=16):
    dataset = tf.data.TFRecordDataset(input_file) \
        .batch(batch_size)
    next_element = tf.compat.v1.data.make_one_shot_iterator(dataset) \
        .get_next()
    with tf.Session() as sess:
        with codecs.open(output_file, "w", 'utf-8') as f:
            while True:
                try:
                    batch_data = sess.run(next_element)
                except Exception as e:
                    print("done")
                    break
                for item in batch_data:
                    vw_str = map_fn(item)
                    f.write("%s\n" % vw_str)
            return True


class SyncConvertDataBlock(object):
    def __init__(self, meta_path, data_path, time_stamp, **kwargs):
        super(SyncConvertDataBlock).__init__()
        self.meta_path = meta_path
        self.data_path = data_path
        self.data_source_name = (self.data_path.split("/")[-1]).split(".")[0]
        self.time_stamp = time_stamp
        self.tf_read = tf.io.tf_record_iterator
        self.data_path_vw_bas_dir = data_path_vw_bas_dir
        self.tmp_path = "/tmp"

    def sync_convert_data_block(self):
        meta_iter = self.tf_read(self.meta_path)
        meta_info = text_format.Parse(next(meta_iter),
                                      data_join_service_pb2.DataBlockMeta())
        logging.info('meta info block_id: {0}'.format(meta_info.block_id))
        logging.info('meta info partition_id: {0}'.format(meta_info.partition_id))

        json_body = dict(start_time=meta_info.start_time,
                         end_time=meta_info.end_time,
                         # example_ids=json.dumps([value.decode("utf-8") for value in data_block_meta.example_ids]),
                         leader_start_index=meta_info.leader_start_index,
                         leader_end_index=meta_info.leader_end_index,
                         follower_restart_index=meta_info.follower_restart_index,
                         data_block_index=meta_info.data_block_index,
                         dfs_data_block_dir=self.data_path,
                         create_status=2,
                         consumed_status=1,
                         data_source_name=self.data_source_name
                         )
        # create datablock
        response_json = wrap_data_transfer_api(
            method='POST',
            endpoint='/v1/data/{0}/{1}/{2}/create/data/block'.format(
                meta_info.block_id,
                meta_info.partition_id,
                meta_info.file_version),
            json_body=json_body,
        )


class StartSyncConvertDataBlock(object):
    @staticmethod
    def run_task():
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--time_stamp', required=True, type=str, help="time_stamp")
        parser.add_argument('-m', '--meta_path', required=True, type=str, help="meta_path")
        parser.add_argument('-p', '--data_path', required=True, type=str, help="data_path")
        args = parser.parse_args()
        time_stamp = args.time_stamp
        meta_path = args.meta_path
        data_path = args.data_path
        SyncConvertDataBlock(meta_path, data_path, time_stamp).sync_convert_data_block()


if __name__ == '__main__':
    StartSyncConvertDataBlock().run_task()
