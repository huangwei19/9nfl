// Copyright (c) 2019 JD, Inc.
#ifndef SERVICES_EXTERNAL_SERVICE_IMPL_H_
#define SERVICES_EXTERNAL_SERVICE_IMPL_H_

#include <iostream>
#include <memory>
#include <string>
#include <grpcpp/grpcpp.h>
#include "glog/logging.h"
#include <gflags/gflags.h>

#include "proto/external_service.grpc.pb.h"
#include "proto/internal_service.grpc.pb.h"
#include "common/fl_gflags.h"
#include "services/common.h"
#include "resource/resource.h"

namespace fl {

class SchedulerServiceImpl final : public ::fedlearner::common::Scheduler::Service {
 public:
  grpc::Status SubmitTrain(
    grpc::ServerContext* context,
    const ::fedlearner::common::TrainRequest* request,
    ::fedlearner::common::Status* response) override;
 private:
  bool CheckModelInfo(const ::fedlearner::common::TrainRequest &request,
                      const ::jdfl::AppInfo &app_info);
};

struct TaskInfo {
  ::fedlearner::common::AppSynRequest request;
  ::jdfl::AppInfo app_info;
};

class StateSynServiceImpl final : public ::fedlearner::common::StateSynService::Service {
 public:
  grpc::Status Syn(
    grpc::ServerContext* context,
    const ::fedlearner::common::AppSynRequest* request,
    ::fedlearner::common::Status* response) override;
 private:
  static void WaitForServiceRegistered(TaskInfo *task);
};

}  // namespace fl

#endif
