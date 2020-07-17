// Copyright (c) 2019 JD, Inc.
#ifndef RESOURCE_RESOURCE_H
#define RESOURCE_RESOURCE_H

#include <memory>
#include <string>
#include "resource/base_executor.h"
#include "resource/hiredis_executor.h"
#include "resource/coordinator_executor.h"

namespace resource {

class Resource {
 public:
  Resource() {}
  virtual ~Resource() {}

  bool Init();

  static Resource* Instance() {
    return instance_.get();
  }

  static bool InitInstance();

  // resource
  HiRedisExecutor* redis_resource() {
    return hiredis_executor_.get();
  }

  std::shared_ptr<grpc::Channel> coordinator_channel() {
    return coordinator_executor_->GetChannel();
  }

 private:
  static std::shared_ptr<Resource> instance_;

  std::shared_ptr<HiRedisExecutor> hiredis_executor_;
  std::shared_ptr<CoordinatorExecutor> coordinator_executor_;
};

}

#endif 
