#ifndef SERVICES_CHECK_APP_STATUS_H
#define SERVICES_CHECK_APP_STATUS_H

#include <set>
#include <memory>
#include "common/util.h"

namespace jdfl {

class CheckAppStatus {
 public:
  static CheckAppStatus* Instance() {
    return instance_.get();
  }

  static void InitInstance() {
    if (nullptr == instance_.get()) 
      instance_.reset(new CheckAppStatus());
  }
  
  void DoCheckAppStatus();
  void AddAppId(const std::string& app_id);
  void DeleteAppId(std::vector<std::string> app_id_arr);

 private:
  CheckAppStatus() {
    app_id_set_.clear();
    pthread_rwlock_init(&rw_lock_, NULL);
  }
  static std::shared_ptr<CheckAppStatus> instance_;
  pthread_rwlock_t rw_lock_;
  std::set<std::string> app_id_set_;
};

void RunCheckAppStatus();

}  // namespace jdfl

#endif
