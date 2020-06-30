
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/shape_inference.h"
#include "tensorflow/core/framework/common_shape_fns.h"

using namespace tensorflow;
using shape_inference::InferenceContext;
using shape_inference::ShapeHandle;

REGISTER_OP("FlChannelConnect")
  .Output("status_code: int32")
  .Output("status_message: string")
  .SetIsStateful()
  .Attr("config_proto: string = ''")
  ;

REGISTER_OP("FlWaitPeerReady")
  .Output("status_code: int32")
  .Output("status_message: string")
  .SetIsStateful()
  .Attr("config_proto: string = ''")
  ;

REGISTER_OP("FlChannelHeartbeat")
  .Output("status_code: int32")
  .Output("status_message: string")
  .SetIsStateful()
  .Attr("config_proto: string = ''")
  ;

