// Copyright (c) 2019 JD, Inc.
#include <memory>
#include <string>
#include "resource/resource.h"

namespace resource {

std::shared_ptr<Resource> Resource::instance_;

bool Resource::Init() {
  // db
  hiredis_executor_.reset(new HiRedisExecutor());
  // 1.5s
  struct timeval timeout = { 1, 500000 };
  if (!hiredis_executor_->Init(FLAGS_redis_hostname, FLAGS_redis_port, timeout)) {
    LOG(ERROR) << "redis init fail!";
    return false;
  }

  // coordinator
  coordinator_executor_.reset(new CoordinatorExecutor());
  if (!coordinator_executor_->Init()) {
    LOG(ERROR) << "coordinator init fail!";
    return false;
  }


  return true;
}

bool Resource::InitInstance() {
  if (nullptr == instance_.get()) {
    instance_.reset(new Resource());
    return instance_->Init();
  }
  return true;
}

}
