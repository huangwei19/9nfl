# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from DataJoin.common import trainer_master_service_pb2 as fedlearner_dot_common_dot_trainer__master__service__pb2


class TrainerMasterServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.RequestDataBlock = channel.unary_unary(
        '/DataJoin.common.TrainerMasterService/RequestDataBlock',
        request_serializer=fedlearner_dot_common_dot_trainer__master__service__pb2.DataBlockRequest.SerializeToString,
        response_deserializer=fedlearner_dot_common_dot_trainer__master__service__pb2.DataBlockResponse.FromString,
        )


class TrainerMasterServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def RequestDataBlock(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_TrainerMasterServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'RequestDataBlock': grpc.unary_unary_rpc_method_handler(
          servicer.RequestDataBlock,
          request_deserializer=fedlearner_dot_common_dot_trainer__master__service__pb2.DataBlockRequest.FromString,
          response_serializer=fedlearner_dot_common_dot_trainer__master__service__pb2.DataBlockResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'DataJoin.common.TrainerMasterService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
