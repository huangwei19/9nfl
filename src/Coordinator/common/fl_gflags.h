#ifndef FL_COMMON_FL_GFLAGS
#define FL_COMMON_FL_GFLAGS

#include "gflags/gflags.h"

DECLARE_int32(port);
DECLARE_string(platform);

DECLARE_int32(lock_timeout_s);
DECLARE_int32(lock_times);
// proxy
DECLARE_string(proxy_url);
// coordinator domain
DECLARE_string(coordinator_domain);
// proxy domain
DECLARE_string(proxy_domain);
// wait for registered
DECLARE_int32(wait_registered_time_ms);
// redis
DECLARE_string(redis_hostname);
DECLARE_int32(redis_port);


#endif
