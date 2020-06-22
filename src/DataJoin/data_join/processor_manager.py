# coding: utf-8

import threading
import logging
import time
import traceback


class ProcessorManager(object):
    def __init__(self, impl_processor_name, impl_processor,
                 impl_condition, impl_time_span):
        self._impl_processor_name = impl_processor_name
        self._lock = threading.Lock()
        self._impl_time_span = impl_time_span
        assert self._impl_time_span > 0, "impl time span is invalid:{0}".format(impl_time_span)
        self._condition = threading.Condition(self._lock)
        self._impl_condition = impl_condition
        self._impl_processor = impl_processor
        self._pass_impl_processor = False
        self._threading = None
        self._inactive_status = False
        self._para_tuple = tuple()
        self._para_dict = dict()

    def active_processor(self):
        with self._lock:
            assert self._threading is None, 'processor {0} is in active'.format(self._impl_processor_name)
            assert not self._inactive_status, 'processor {0} is in inactive'.format(self._impl_processor_name)
            self._threading = threading.Thread(target=self.implementor,
                                               name=self._impl_processor_name)
            self._threading.start()

    def inactive_processor(self):
        thread = None
        with self._lock:
            if self._threading is not None and not self._inactive_status:
                self._inactive_status = True
                self._condition.notify()
                thread = self._threading
                self._threading = None
        if thread is not None:
            thread.join()

    def enable_processor(self):
        with self._condition:
            self._condition.notify()
            self._pass_impl_processor = False

    def is_inactive(self):
        with self._lock:
            return self._inactive_status

    def build_impl_processor_parameter(self, *args, **kwargs):
        with self._lock:
            self._para_tuple = args
            self._para_dict = kwargs

    def entry_impl_processor(self):
        with self._lock:
            if self._pass_impl_processor:
                return True
        return not self._impl_condition()

    def acquire_impl_processor_parameter(self):
        with self._lock:
            parameter = (self._para_tuple, self._para_dict)
            self._para_tuple = tuple()
            self._para_dict = dict()
            return parameter

    def implementor(self):
        impl_count = 0
        while not self.is_inactive():
            impl_time_point = time.time()
            while self.entry_impl_processor():
                with self._lock:
                    if self._inactive_status:
                        return
                    if self._impl_time_span is None:
                        self._condition.wait()
                    else:
                        wait_time_span = (self._impl_time_span -
                                          (time.time() - impl_time_point))
                        if wait_time_span > 0:
                            self._condition.wait(wait_time_span)
                        else:
                            self._pass_impl_processor = False
                            impl_time_point = time.time()
            try:
                with self._lock:
                    self._pass_impl_processor = self._impl_time_span is not None
                parameter = self.acquire_impl_processor_parameter()
                self._impl_processor(*(parameter[0]), **(parameter[1]))
            except Exception as e:
                logging.error("processor: %s implement %d rounds with exception",
                              self._impl_processor_name, impl_count)
                logging.info("processor: error msg is: %s" % traceback.print_exc(e))
            else:
                logging.info("processor: %s implement %d round", self._impl_processor_name, impl_count)
            impl_count += 1
        logging.warning("processor: %s is going to stop", self._impl_processor_name)
