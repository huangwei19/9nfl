// Copyright (c) 2019 JD, Inc.
#ifndef SRC_COORDINATOR_SERVICES_INVOKE_MODULE_H_
#define SRC_COORDINATOR_SERVICES_INVOKE_MODULE_H_

#include <gflags/gflags.h>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <string>
#include "glog/logging.h"

#include "proto/external_service.grpc.pb.h"
#include "common/fl_gflags.h"
#include "services/common.h"
#include "resource/resource.h"

namespace jdfl {
class InvokeModule {
 public:
  explicit InvokeModule(const ::jdfl::AppInfo& app_info): app_info_(app_info),
      syn_stub_(::fedlearner::common::StateSynService::NewStub(
        resource::Resource::Instance()->coordinator_channel())),
      submit_train_stub_(::fedlearner::common::Scheduler::NewStub(
        resource::Resource::Instance()->coordinator_channel())) {
    log_common_ = "app_id: " + app_info.conf_info().app_id() +
                 " model_uri: " + app_info.conf_info().model_uri();
  }
  ~InvokeModule() {
  }
  grpc::Status InvokeSubmitTrain();
  grpc::Status InvokeSyn(grpc::ClientContext* context,
                         const ::fedlearner::common::AppSynRequest& request,
                         ::fedlearner::common::Status* reply);
 private:
  ::jdfl::AppInfo app_info_;
  std::string log_common_;
  std::unique_ptr<::fedlearner::common::StateSynService::Stub> syn_stub_;
  std::unique_ptr<::fedlearner::common::Scheduler::Stub> submit_train_stub_;
};

}  // namespace jdfl

#endif  // SRC_COORDINATOR_SERVICES_INVOKE_MODULE_H_
