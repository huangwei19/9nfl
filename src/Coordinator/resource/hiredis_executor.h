// Copyright (c) 2019 JD, Inc.
#ifndef RESOURCE_HIREDIS_EXECUTOR_H
#define RESOURCE_HIREDIS_EXECUTOR_H

#include <vector>
#include <memory>
#include <string>
#include <mutex>
#include "glog/logging.h"
#include "common/fl_gflags.h"
#include "hiredis/hiredis.h"

namespace resource {

class HiRedisExecutor {
 public:
  HiRedisExecutor() {}
  virtual ~HiRedisExecutor() {
    redisFree(redis_ctx_);
  }

  virtual bool Init(
    const std::string &hostname, int port, const struct timeval &timeout);

  bool Lock(const std::string &str, int lock_timeout_s);
  void Unlock(const std::string &str);

  bool Get(const std::string &key, std::string *value);
  bool Set(const std::string &key, const std::string &value);
  bool Mset(const std::vector<std::string> &keys,
            const std::vector<std::string> &values);
  bool SetEx(const std::string &key, const std::string &value, int time_s);
  void Del(const std::string &key);
  void Del(const std::vector<std::string> &keys);

 private:
  bool CheckReply(redisReply *reply);
  redisContext *redis_ctx_ = nullptr;
  const std::string lock_str_ = "fl_lock_";

  std::mutex mtx_;
};

}  // namespace resource

#endif
