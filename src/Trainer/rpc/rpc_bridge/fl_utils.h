
#ifndef JDFL_FL_UTILS_H_
#define JDFL_FL_UTILS_H_

#include <unordered_map>
#include <iostream>
#include <string>
#include <sstream>
#include <stdio.h>
#include <stdlib.h>
#include <chrono>
#include <cstdint>
#include <string>

#include "tensorflow/core/platform/env.h"

using namespace ::tensorflow;

namespace jdfl {

int PrepareFile(const string& hdfs_src, std::string& out_fname);

int CleanFile( const std::string& fname);

const std::string& LocalFileDir();

int32_t FlDebugging();

}

#endif 
