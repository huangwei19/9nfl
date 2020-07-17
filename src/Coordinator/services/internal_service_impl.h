// Copyright (c) 2019 JD, Inc.
#ifndef SERVICES_INTERNALSERVICE_IMPL_H_
#define SERVICES_INTERNALSERVICE_IMPL_H_

#include <iostream>
#include <memory>
#include <string>
#include <grpcpp/grpcpp.h>
#include "glog/logging.h"
#include <gflags/gflags.h>

#include "proto/internal_service.grpc.pb.h"
#include "common/fl_gflags.h"
#include "services/common.h"
#include "resource/resource.h"

namespace jdfl {

class StartApplicationImpl final : public StartApplication::Service {
 public:
  StartApplicationImpl() {}
  ~StartApplicationImpl() {}
  virtual grpc::Status StartApplication(grpc::ServerContext* context,
                                        const ::jdfl::ModelURI* request,
                                        ::jdfl::Status* response)override;
};
class InternalServiceImpl final : public PairService::Service {
 public:
  InternalServiceImpl() {}
  virtual ~InternalServiceImpl() {}
  virtual grpc::Status RegisterUUID(grpc::ServerContext* context,
                                    const ::jdfl::Request* request,
                                    ::jdfl::Status* response) override;
  virtual grpc::Status GetPairInfo(grpc::ServerContext* context,
                                   const ::jdfl::Request* request,
                                   ::jdfl::PairInfoResponse* response) override;
 private:
  bool ReplaceUUIDForNewIp(
    const ::jdfl::Request &request, ::jdfl::AppInfo *app_info);
};

}  // namespace jdfl

#endif
