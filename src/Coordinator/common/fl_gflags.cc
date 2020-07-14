#include "common/fl_gflags.h"

DEFINE_int32(port, 6666, "TCP Port of this server");
DEFINE_string(platform, "", "platform name.");

// lock
DEFINE_int32(lock_timeout_s, 1, "lock timeout");
DEFINE_int32(lock_times, 20, "lock times");
// coordinator domain
DEFINE_string(coordinator_domain, "", "coordinator_domain or ip and port");
// proxy domain
DEFINE_string(proxy_domain, "", "proxy_domain or ip and port");
// wait for registered
DEFINE_int32(wait_registered_time_ms, 1000, "");
// redis
DEFINE_string(redis_hostname, "127.0.0.1", "redis hostname");
DEFINE_int32(redis_port, 6379, "redis port");
