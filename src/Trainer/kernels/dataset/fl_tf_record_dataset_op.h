
#include <string>

#ifndef TENSORFLOW_CONTRIB_JDFL_KERNELS_DATASET_FL_TF_RECORD_DATASET_OP_H_
#define TENSORFLOW_CONTRIB_JDFL_KERNELS_DATASET_FL_TF_RECORD_DATASET_OP_H_

#include "tensorflow/core/framework/dataset.h"

#include "tensorflow/contrib/jdfl/rpc/proto/dc_agent.pb.h"
#include "tensorflow/contrib/jdfl/rpc/rpc_bridge/fl_utils.h"
#include "tensorflow/contrib/jdfl/rpc/rpc_bridge/rpc_dc_agent.h"

using namespace ::tensorflow;

namespace jdfl {

class FlTFRecordDatasetOp : public UnaryDatasetOpKernel {
 public:
  static constexpr const char* const kDatasetType = "FlTFRecord";
  static constexpr const char* const kInputDataset = "input_dataset";
  static constexpr const char* const kFileType = "file_type";
  static constexpr const char* const kCompressionType = "compression_type";
  static constexpr const char* const kBufferSize = "buffer_size";
  static constexpr const char* const kOutputTypes = "output_types";
  static constexpr const char* const kOutputShapes = "output_shapes";

  explicit FlTFRecordDatasetOp(OpKernelConstruction* ctx);

 protected:
  void MakeDataset(OpKernelContext* ctx, DatasetBase* input,
                   DatasetBase** output) override;

 private:
  class Dataset;
  string file_type_;
};

}  // namespace jdfl

#endif  // TENSORFLOW_CONTRIB_JDFL_KERNELS_DATASET_FL_TF_RECORD_DATASET_OP_H_
