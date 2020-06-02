# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Training helper that checkpoints models and creates session."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import numpy as np

from tensorflow.python.client import session
from tensorflow.python.distribute import distribution_strategy_context
from tensorflow.python.framework import errors
from tensorflow.python.framework import ops
from tensorflow.python.platform import tf_logging as logging
from tensorflow.python.training import checkpoint_management
from tensorflow.python.training import session_manager as sm
from tensorflow.python.util.tf_export import tf_export


def _restore_checkpoint_patch(self,
                        master,
                        saver=None,
                        checkpoint_dir=None,
                        checkpoint_filename_with_path=None,
                        wait_for_checkpoint=False,
                        max_wait_secs=7200,
                        config=None):

  self._target = master

  # This is required to so that we initialize the TPU device before
  # restoring from checkpoint since we'll be placing variables on the device
  # and TPUInitialize wipes out the memory of the device.
  strategy = distribution_strategy_context.get_strategy()
  if strategy and hasattr(strategy.extended,
                          "_experimental_initialize_system"):
    strategy.extended._experimental_initialize_system()  # pylint: disable=protected-access

  sess = session.Session(self._target, graph=self._graph, config=config)
  if checkpoint_dir and checkpoint_filename_with_path:
    raise ValueError("Can not provide both checkpoint_dir and "
                     "checkpoint_filename_with_path.")
  
  is_ready_for_local_init, _ = self._model_ready_for_local_init(sess)
  if is_ready_for_local_init:
    logging.info("*****************************")
    logging.info("*** SKIP RESTORE CHECKPOINT.")
    logging.info("*****************************")
    return sess, True
  
  # If either saver or checkpoint_* is not specified, cannot restore. Just
  # return.
  if not saver or not (checkpoint_dir or checkpoint_filename_with_path):
    return sess, False

  if checkpoint_filename_with_path:
    saver.restore(sess, checkpoint_filename_with_path)
    return sess, True

  # Waits up until max_wait_secs for checkpoint to become available.
  wait_time = 0
  ckpt = checkpoint_management.get_checkpoint_state(checkpoint_dir)
  while not ckpt or not ckpt.model_checkpoint_path:
    if wait_for_checkpoint and wait_time < max_wait_secs:
      logging.info("Waiting for checkpoint to be available.")
      time.sleep(self._recovery_wait_secs)
      wait_time += self._recovery_wait_secs
      ckpt = checkpoint_management.get_checkpoint_state(checkpoint_dir)
    else:
      return sess, False

  # Loads the checkpoint.
  saver.restore(sess, ckpt.model_checkpoint_path)
  saver.recover_last_checkpoints(ckpt.all_model_checkpoint_paths)
  return sess, True

sm.SessionManager._restore_checkpoint = _restore_checkpoint_patch