# coding: utf-8

import logging
import tensorflow.compat.v1 as tf
from DataJoin.config import Invalid_ExampleId, Invalid_EventTime
from DataJoin.utils.data_process import tf_record_iterator_factory
from DataJoin.data_join.data_iterator_builder.data_iterator import DataIterator
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
                self._event_time = Invalid_EventTime
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
                self._example_id = Invalid_ExampleId
        return self._example_id


class TfRecordDataIterator(DataIterator):
    @classmethod
    def iterator_name(cls):
        return 'TF_RECORD_ITERATOR'

    def _data_iterator_factory(self, file_path):
        with tf_record_iterator_factory(file_path) as record_iter:
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

