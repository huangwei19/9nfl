
#include "tensorflow/core/framework/common_shape_fns.h"
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/shape_inference.h"

REGISTER_OP("FlBridgeServerInit")
    .Input("server_address: string")
    .Input("appli_id: string")
    .Input("rank_id: int32")
    .Input("role_def: string")
    .Input("rpc_service_type: int32")  // kinds of service method(Unary or
                                       // Bidirectional streaming RPCs)
    .Input("contex_metadata: string")
    .SetIsStateful()
    .Attr("config_proto: string = ''");

REGISTER_OP("FlRpcChannelInit")
    .Input("target_address: string")
    .SetIsStateful()
    .Attr("channel_type: {'TRAIN', 'DATA'}")
    .Attr("config_proto: string = ''");
