
#ifndef TENSORFLOW_CONTRIB_JDFL_RPC_RPC_BRIDGE_FL_UTILS_H_
#define TENSORFLOW_CONTRIB_JDFL_RPC_RPC_BRIDGE_FL_UTILS_H_

#include <stdio.h>
#include <stdlib.h>
#include <cstdint>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>

#include "tensorflow/core/platform/env.h"


namespace jdfl {

int PrepareFile(const std::string& hdfs_src, std::string* out_fname);

int CleanFile(const std::string& fname);

const std::string& LocalFileDir();

int32_t FlDebugging();
}

#endif  // TENSORFLOW_CONTRIB_JDFL_RPC_RPC_BRIDGE_FL_UTILS_H_
