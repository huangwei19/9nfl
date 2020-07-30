// Copyright (c) 2019 JD, Inc.
#ifndef RESOURCE_BASE_EXECUTOR_H
#define RESOURCE_BASE_EXECUTOR_H

#include <memory>
#include <string>
#include "gflags/gflags.h"
#include "common/util.h"

namespace resource {

class BaseExecutor {
 public:
  BaseExecutor() {}
  virtual ~BaseExecutor() {}
  virtual bool Init() = 0;

  std::shared_ptr<grpc::Channel> GetChannel() {
    return channel_;
  }
 protected:
  std::shared_ptr<grpc::Channel> channel_;
};

}  // namespace resource
#endif
