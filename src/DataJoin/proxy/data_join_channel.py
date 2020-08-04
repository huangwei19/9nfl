# coding: utf-8

import os
import collections
import grpc
from DataJoin.config import ModeType
from DataJoin.utils.base import address_valid_checker

inner_proxy = os.environ.get('INTERNAL_PROXY', None)


class _GenericClientInterceptor(grpc.UnaryUnaryClientInterceptor,
                                grpc.UnaryStreamClientInterceptor,
                                grpc.StreamUnaryClientInterceptor,
                                grpc.StreamStreamClientInterceptor):
    def __init__(self, interceptor_function):
        self._fn = interceptor_function

    def intercept_unary_unary(self, continuation, client_call_details,
                              request):
        new_details, new_request_iterator, postprocess = self._fn(
            client_call_details, iter((request,)), False, False)
        response = continuation(new_details, next(new_request_iterator))
        return postprocess(response) if postprocess else response

    def intercept_unary_stream(self, continuation, client_call_details,
                               request):
        new_details, new_request_iterator, postprocess = self._fn(
            client_call_details, iter((request,)), False, True)
        response_it = continuation(new_details, next(new_request_iterator))
        return postprocess(response_it) if postprocess else response_it

    def intercept_stream_unary(self, continuation, client_call_details,
                               request_iterator):
        new_details, new_request_iterator, postprocess = self._fn(
            client_call_details, request_iterator, True, False)
        response = continuation(new_details, new_request_iterator)
        return postprocess(response) if postprocess else response

    def intercept_stream_stream(self, continuation, client_call_details,
                                request_iterator):
        new_details, new_request_iterator, postprocess = self._fn(
            client_call_details, request_iterator, True, True)
        response_it = continuation(new_details, new_request_iterator)
        return postprocess(response_it) if postprocess else response_it


class _ClientCallDetails(
    collections.namedtuple(
        '_ClientCallDetails',
        ('method', 'timeout', 'metadata', 'credentials')),
    grpc.ClientCallDetails):
    pass


def add_header_interceptor(header, value):
    def intercept_call(client_call_details, request_iterator,
                       request_streaming, response_streaming):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        metadata.append((
            header,
            value,
        ))
        client_call_details = _ClientCallDetails(
            client_call_details.method, client_call_details.timeout, metadata,
            client_call_details.credentials)
        return client_call_details, request_iterator, None

    return _GenericClientInterceptor(intercept_call)


def create_data_join_channel(uuid,
                             mode=ModeType.REMOTE,
                             options=None,
                             compression=None):
    if address_valid_checker(uuid):
        return grpc.insecure_channel(uuid, options, compression)

    if mode == ModeType.REMOTE:
        header_adder = add_header_interceptor('uuid', uuid)
        if not inner_proxy:
            raise Exception("inner_proxy is None")
        channel = grpc.insecure_channel(inner_proxy, options, compression)
        return grpc.intercept_channel(channel, header_adder)
    raise Exception("uuid mode type is UnKnown %s" % uuid)
