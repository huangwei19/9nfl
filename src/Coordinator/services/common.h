// Copyright (c) 2019 JD, Inc.
#ifndef SERVICES_COMMON_H_
#define SERVICES_COMMON_H_

#include <iostream>
#include <memory>
#include <string>
#include <grpcpp/grpcpp.h>
#include "glog/logging.h"
#include <gflags/gflags.h>

#include "proto/internal_service.grpc.pb.h"
#include "proto/external_service.grpc.pb.h"
#include "common/fl_gflags.h"
#include "resource/resource.h"

namespace jdfl {

bool GetJsonConfFromRedis(const std::string& model_uri,
                          const std::string& version,
                          ::jdfl::AppInfo *app_info);
bool RegisterCoodinator();

bool StartK8S(const std::string& app_id);
bool StartK8SFromAppInfo(const ::jdfl::AppInfo &app_info);
bool StopK8S(const std::string& app_id);
int CheckK8S(const std::string& app_id);
 
bool CheckAppInfo(const AppInfo& app_info);

bool SetAppInfoToRedis(const ::jdfl::AppInfo& app_info);

bool DeleteAppInfoInRedis(const std::string &app_id);

bool GetAppInfoFromRedis(const std::string& app_id,
                         ::jdfl::AppInfo* app_info);

int32_t CheckRegisterNum(const std::string& app_id, ::jdfl::AppInfo* app_info);

}

#endif
