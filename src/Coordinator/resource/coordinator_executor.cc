// Copyright (c) 2019 JD, Inc.
#include <memory>
#include <string>
#include "resource/coordinator_executor.h"

namespace resource {

bool CoordinatorExecutor::Init() {
  channel_ = grpc::CreateChannel(FLAGS_proxy_domain, grpc::InsecureChannelCredentials());
  if (!channel_) {
    LOG(ERROR) << "Init coordinator fail!";
    return false;
  }
  return true;
}

}
