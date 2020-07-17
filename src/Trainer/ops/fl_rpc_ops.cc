
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/shape_inference.h"
#include "tensorflow/core/framework/common_shape_fns.h"

using namespace tensorflow;
using shape_inference::InferenceContext;
using shape_inference::ShapeHandle;

REGISTER_OP("FlTensorRecv")
  //.Input("input_proto: string")
  .Output("output: T")
  .SetIsStateful()
  .Attr("T: {float, int64} = DT_FLOAT")
  .Attr("max_retries: int = -1")
  .Attr("timeout_in_ms: int = 0")
  .Attr("datamsg_rname: string = 'output:0'") // recv tensor name
  .Attr("datamsg_type: string = '/FlDataMessage'")
  ;

REGISTER_OP("FlTensorRecvWithGradBp")
  //.Input("input_proto: string")
  .Output("output: float")
  .SetIsStateful()
  .Attr("max_retries: int = -1")
  .Attr("timeout_in_ms: int = 0")
  .Attr("datamsg_rname: string = 'output:0'") // recv tensor name
  .Attr("datamsg_type: string = '/FlDataMessage'")
  .Attr("grad_sname: string = 'grad:0'") // the registered gradient send tensor name
  ;

REGISTER_OP("FlTensorRecvWithFakeInput")
  //.Input("input_proto: string")
  .Input("input_fake: float")
  .Output("output: float")
  .SetIsStateful()
  .Attr("max_retries: int = -1")
  .Attr("timeout_in_ms: int = 0")
  .Attr("datamsg_rname: string = 'output:0'")  // recv tensor name
  .Attr("datamsg_type: string = '/FlDataMessage'")
  .Attr("grad_sname: string = 'grad:0'") // the registered gradient send tensor name
  ;

REGISTER_OP("FlGradRecv")
  //.Input("input_proto: string")
  .Output("output: float")
  .SetIsStateful()
  .Attr("max_retries: int = -1")
  .Attr("timeout_in_ms: int = 0")
  .Attr("datamsg_rname: string = 'grad:0'")     // recv tensor name
  .Attr("datamsg_type: string = '/FlDataMessage'")
  ;

REGISTER_OP("FlTrainStart")
  .Input("input_proto: string")
  .Output("output: string")
  .SetIsStateful()
  .Attr("max_retries: int = -1")
  .Attr("timeout_in_ms: int = 0")
  .Attr("datamsg_type: string = '/FlTrainStart'")
  ;

REGISTER_OP("FlTrainFollow")
  .Output("status_code: int32")
  .Output("status_message: string")
  .SetIsStateful()
  .Attr("max_retries: int = 3")
  .Attr("timeout_in_ms: int = 0")
  .Attr("datamsg_type: string = '/FlTrainStart'")
  ;

REGISTER_OP("FlTensorSend")
  //.Input("input_proto: string")
  .Input("input: T")
  .Output("output: T")
  .SetIsStateful()
  .Attr("T: {float, int64} = DT_INT64")
  .Attr("max_retries: int = -1")
  .Attr("timeout_in_ms: int = 0")
  .Attr("datamsg_sname: string = 'output:0'")  // sent tensor name
  .Attr("datamsg_type: string = '/FlDataMessage'")
  ;

REGISTER_OP("FlGradBackpropRequest")
  //.Input("input_proto: string")
  .Input("input: float")
  .Output("output: float")
  .SetIsStateful()
  .Attr("max_retries: int = -1")
  .Attr("timeout_in_ms: int = 0")
  .Attr("datamsg_sname: string = 'grad:0'")   // sent tensor name
  .Attr("datamsg_type: string = '/FlDataMessage'")
  ;

REGISTER_OP("FlTensorSendRecv")
  .Input("input: float")
  .Output("output: float")
  .SetIsStateful()
  .Attr("max_retries: int = -1")
  .Attr("timeout_in_ms: int = 0")
  .Attr("datamsg_sname: string = 'output:0'")   // sent tensor name
  .Attr("datamsg_rname: string = 'grad:0'")     // recv tensor name
  .Attr("datamsg_type: string = '/FlDataMessage'")
  ;

REGISTER_OP("FlTrainStepCommit")
  //.Input("input_proto: string")
  .SetIsStateful()
  .Attr("max_retries: int = -1")
  .Attr("timeout_in_ms: int = 0")
  .Attr("datamsg_type: string = '/FlStepCommit'")
  ;
