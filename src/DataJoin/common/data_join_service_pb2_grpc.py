# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from DataJoin.common import common_pb2 as fedlearner_dot_common_dot_common__pb2
from DataJoin.common import data_join_service_pb2 as fedlearner_dot_common_dot_data__join__service__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


class DataJoinMasterServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetDataSource = channel.unary_unary(
        '/fedlearner.common.DataJoinMasterService/GetDataSource',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_common__pb2.DataSource.FromString,
        )
    self.GetDataSourceStatus = channel.unary_unary(
        '/fedlearner.common.DataJoinMasterService/GetDataSourceStatus',
        request_serializer=fedlearner_dot_common_dot_data__join__service__pb2.DataSourceRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.DataSourceStatus.FromString,
        )
    self.AbortDataSource = channel.unary_unary(
        '/fedlearner.common.DataJoinMasterService/AbortDataSource',
        request_serializer=fedlearner_dot_common_dot_data__join__service__pb2.DataSourceRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_common__pb2.Status.FromString,
        )
    self.RequestJoinPartition = channel.unary_unary(
        '/fedlearner.common.DataJoinMasterService/RequestJoinPartition',
        request_serializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataResponse.FromString,
        )
    self.FinishJoinPartition = channel.unary_unary(
        '/fedlearner.common.DataJoinMasterService/FinishJoinPartition',
        request_serializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_common__pb2.Status.FromString,
        )
    self.QueryRawDataManifest = channel.unary_unary(
        '/fedlearner.common.DataJoinMasterService/QueryRawDataManifest',
        request_serializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataManifest.FromString,
        )
    self.FinishRawData = channel.unary_unary(
        '/fedlearner.common.DataJoinMasterService/FinishRawData',
        request_serializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_common__pb2.Status.FromString,
        )
    self.AddRawData = channel.unary_unary(
        '/fedlearner.common.DataJoinMasterService/AddRawData',
        request_serializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_common__pb2.Status.FromString,
        )


class DataJoinMasterServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetDataSource(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetDataSourceStatus(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def AbortDataSource(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def RequestJoinPartition(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def FinishJoinPartition(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def QueryRawDataManifest(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def FinishRawData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def AddRawData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DataJoinMasterServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetDataSource': grpc.unary_unary_rpc_method_handler(
          servicer.GetDataSource,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=fedlearner_dot_common_dot_common__pb2.DataSource.SerializeToString,
      ),
      'GetDataSourceStatus': grpc.unary_unary_rpc_method_handler(
          servicer.GetDataSourceStatus,
          request_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.DataSourceRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_data__join__service__pb2.DataSourceStatus.SerializeToString,
      ),
      'AbortDataSource': grpc.unary_unary_rpc_method_handler(
          servicer.AbortDataSource,
          request_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.DataSourceRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_common__pb2.Status.SerializeToString,
      ),
      'RequestJoinPartition': grpc.unary_unary_rpc_method_handler(
          servicer.RequestJoinPartition,
          request_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataResponse.SerializeToString,
      ),
      'FinishJoinPartition': grpc.unary_unary_rpc_method_handler(
          servicer.FinishJoinPartition,
          request_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_common__pb2.Status.SerializeToString,
      ),
      'QueryRawDataManifest': grpc.unary_unary_rpc_method_handler(
          servicer.QueryRawDataManifest,
          request_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataManifest.SerializeToString,
      ),
      'FinishRawData': grpc.unary_unary_rpc_method_handler(
          servicer.FinishRawData,
          request_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_common__pb2.Status.SerializeToString,
      ),
      'AddRawData': grpc.unary_unary_rpc_method_handler(
          servicer.AddRawData,
          request_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.RawDataRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_common__pb2.Status.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'fedlearner.common.DataJoinMasterService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class DataJoinServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.StartPartition = channel.unary_unary(
        '/fedlearner.common.DataJoinService/StartPartition',
        request_serializer=fedlearner_dot_common_dot_data__join__service__pb2.StartPartitionRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.StartPartitionResponse.FromString,
        )
    self.SyncPartition = channel.unary_unary(
        '/fedlearner.common.DataJoinService/SyncPartition',
        request_serializer=fedlearner_dot_common_dot_data__join__service__pb2.SyncPartitionRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_common__pb2.Status.FromString,
        )
    self.FinishPartition = channel.unary_unary(
        '/fedlearner.common.DataJoinService/FinishPartition',
        request_serializer=fedlearner_dot_common_dot_data__join__service__pb2.FinishPartitionRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.FinishPartitionResponse.FromString,
        )


class DataJoinServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def StartPartition(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SyncPartition(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def FinishPartition(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DataJoinServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'StartPartition': grpc.unary_unary_rpc_method_handler(
          servicer.StartPartition,
          request_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.StartPartitionRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_data__join__service__pb2.StartPartitionResponse.SerializeToString,
      ),
      'SyncPartition': grpc.unary_unary_rpc_method_handler(
          servicer.SyncPartition,
          request_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.SyncPartitionRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_common__pb2.Status.SerializeToString,
      ),
      'FinishPartition': grpc.unary_unary_rpc_method_handler(
          servicer.FinishPartition,
          request_deserializer=fedlearner_dot_common_dot_data__join__service__pb2.FinishPartitionRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_data__join__service__pb2.FinishPartitionResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'fedlearner.common.DataJoinService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
