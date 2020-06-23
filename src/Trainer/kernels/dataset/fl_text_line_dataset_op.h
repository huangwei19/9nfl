
#ifndef JDFL_TEXT_LINE_DATASET_OP_H_
#define JDFL_TEXT_LINE_DATASET_OP_H_

#include "tensorflow/core/framework/dataset.h"

#include "tensorflow/contrib/jdfl/rpc/proto/dc_agent.pb.h"
#include "tensorflow/contrib/jdfl/rpc/rpc_bridge/rpc_dc_agent.h"
#include "tensorflow/contrib/jdfl/rpc/rpc_bridge/fl_utils.h"

using namespace ::tensorflow;

namespace jdfl {

class FlTextLineDatasetOp : public UnaryDatasetOpKernel {
 public:
  static constexpr const char* const kDatasetType = "TextLine";
  static constexpr const char* const kCompressionType = "compression_type";
  static constexpr const char* const kBufferSize = "buffer_size";

  explicit FlTextLineDatasetOp(OpKernelConstruction* ctx);

 protected:
  void MakeDataset(OpKernelContext* ctx, DatasetBase* input,
                   DatasetBase** output) override;

 private:
  class Dataset;
};

}  // namespace jdfl


#endif  // JDFL_TEXT_LINE_DATASET_OP_H_
