
#ifndef TENSORFLOW_CONTRIB_JDFL_KERNELS_DATASET_FL_GRPC_FETCH_DATASET_OP_H_
#define TENSORFLOW_CONTRIB_JDFL_KERNELS_DATASET_FL_GRPC_FETCH_DATASET_OP_H_

#include "tensorflow/core/framework/dataset.h"

#include "tensorflow/contrib/jdfl/rpc/proto/dc_agent.pb.h"
#include "tensorflow/contrib/jdfl/rpc/rpc_bridge/fl_utils.h"
#include "tensorflow/contrib/jdfl/rpc/rpc_bridge/rpc_dc_agent.h"

using namespace ::tensorflow;

namespace jdfl {

class FlGrpcFetchDatasetOp : public DatasetOpKernel {
 public:
  static constexpr const char* const kDatasetType = "FlGrpcFetch";
  static constexpr const char* const kRoleDef = "role_def";
  static constexpr const char* const kMaxRetries = "max_retries";
  static constexpr const char* const kTimeoutInMs = "timeout_in_ms";

  explicit FlGrpcFetchDatasetOp(OpKernelConstruction* ctx);

 protected:
  void MakeDataset(OpKernelContext* ctx, DatasetBase** output) override;

 private:
  class Dataset;
  int max_retries_;
  int timeout_in_ms_;
};

}  // namespace jdfl

#endif  // TENSORFLOW_CONTRIB_JDFL_KERNELS_DATASET_FL_GRPC_FETCH_DATASET_OP_H_
