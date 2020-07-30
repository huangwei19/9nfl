// Copyright (c) 2019 JD, Inc.
#ifndef SRC_COORDINATOR_SERVICES_INTERNAL_SERVICE_IMPL_H_
#define SRC_COORDINATOR_SERVICES_INTERNAL_SERVICE_IMPL_H_

#include <grpcpp/grpcpp.h>
#include <gflags/gflags.h>
#include <iostream>
#include <memory>
#include <string>
#include "glog/logging.h"

#include "proto/internal_service.grpc.pb.h"
#include "common/fl_gflags.h"
#include "services/common.h"
#include "resource/resource.h"

namespace jdfl {

class StartApplicationImpl final : public StartApplication::Service {
 public:
  StartApplicationImpl() {}
  ~StartApplicationImpl() {}

  grpc::Status StartApplication(
    grpc::ServerContext* context,
    const ::jdfl::ModelURI* request,
    ::jdfl::Status* response) override;
};

class InternalServiceImpl final : public PairService::Service {
 public:
  InternalServiceImpl() {}
  virtual ~InternalServiceImpl() {}

  grpc::Status RegisterUUID(
    grpc::ServerContext* context,
    const ::jdfl::Request* request,
    ::jdfl::Status* response) override;

  grpc::Status GetPairInfo(
    grpc::ServerContext* context,
    const ::jdfl::Request* request,
    ::jdfl::PairInfoResponse* response) override;

 private:
  bool ReplaceUUIDForNewIp(
    const ::jdfl::Request &request, ::jdfl::AppInfo *app_info);
};

}  // namespace jdfl

#endif  // SRC_COORDINATOR_SERVICES_INTERNAL_SERVICE_IMPL_H_
