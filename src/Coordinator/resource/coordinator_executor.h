// Copyright (c) 2019 JD, Inc.
#ifndef RESOURCE_COORDINATOR_EXECUTOR_H
#define RESOURCE_COORDINATOR_EXECUTOR_H

#include <memory>
#include <string>
#include "gflags/gflags.h"
#include "common/fl_gflags.h"
#include "resource/base_executor.h"

namespace resource {

class CoordinatorExecutor : public BaseExecutor {
 public:
  CoordinatorExecutor() {}
  virtual ~CoordinatorExecutor() {}

  virtual bool Init();
};

}
#endif 
