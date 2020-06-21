# coding: utf-8

import logging
from contextlib import contextmanager

import tensorflow.compat.v1 as tf

import DataJoin.data_join.common as common
from DataJoin.data_join.raw_data_iter_impl.raw_data_iter import DataIterator
import traceback


class TfRecordDataItemParser(DataIterator.DataItemParser):
    def __init__(self, item_iter):
        self._item_iter = item_iter
        self._example = None
        self._example_id = None
        self._event_time = None

    def _example_parser(self):
        if self._example is None:
            example = tf.train.Example()
            example.ParseFromString(self._item_iter)
            self._example = example

    @property
    def record(self):
        return self._item_iter

    @property
    def event_time(self):
        if self._event_time is None:
            try:
                self._example_parser()
                feature = self._example.features.feature
                if feature['event_time'].HasField('int64_list'):
                    self._event_time = feature['event_time'].int64_list.value[0]
                if feature['event_time'].HasField('bytes_list'):
                    self._event_time = \
                        int(feature['event_time'].bytes_list.value[0])
            except Exception as e:
                logging.info("Parse event time Failed from {0},"
                             "error msg:{1}".format(self._item_iter,
                                                    traceback.print_exc(str(e))))
                self._event_time = common.InvalidEventTime
        return self._event_time

    @property
    def example_id(self):
        if self._example_id is None:
            try:
                self._example_parser()
                feature = self._example.features.feature
                self._example_id = feature['example_id'].bytes_list.value[0]
            except Exception as e:
                logging.info("Parse example id Failed from {0},"
                             "error msg:{1}".format(self._item_iter,
                                                    traceback.print_exc(str(e))))
                self._example_id = common.InvalidExampleId
        return self._example_id


class TfRecordDataIterator(DataIterator):
    @classmethod
    def iterator_name(cls):
        return 'TF_RECORD_ITERATOR'

    def _data_iterator_factory(self, file_path):
        with common.make_tf_record_iter(file_path) as record_iter:
            for record in record_iter:
                yield TfRecordDataItemParser(record)

    def _reset_data_iterator(self, file_path):
        if file_path is not None:
            data_iterator = self._data_iterator_factory(file_path)
            first_item = next(data_iterator)
            return data_iterator, first_item
        return None, None

    def _visit_next_item(self):
        assert self._data_iterator is not None, "data_iterator should not be None in _next"
        return next(self._data_iterator)


'''
class TfDataSetIter(DataIterator, metaclass=MetaClass):
    @classmethod
    def name(cls):
        return 'TF_DATASET'

    @contextmanager
    def _data_set(self, fpath):
        data_set = None
        expt = None
        try:
            data_set = tf.data.TFRecordDataset(
                [fpath],
                compression_type=self._options.compressed_type,
                num_parallel_reads=4
            )
            data_set = data_set.batch(64)
            yield data_set
        except Exception as e:  # pylint: disable=broad-except
            logging.warning("Failed to access file: %s, reason %s", fpath, e)
            expt = e
        if data_set is not None:
            del data_set
        if expt is not None:
            raise expt

    def _data_iterator_factory(self, fpath):
        with self._data_set(fpath) as data_set:
            for batch in iter(data_set):
                for raw_data in batch.numpy():
                    yield TfRecordDataItemParser(raw_data)

    def _reset_data_iterator(self, file_path):
        if file_path is not None:
            fiter = self._data_iterator_factory(file_path)
            item = next(fiter)
            return fiter, item
        return None, None

    def _next(self):
        assert self._fiter is not None, "_fiter must be not None in _next"
        return next(self._fiter)
'''

