#!/bin/sh
# Copyright 2020 The 9nFL Authors. All Rights Reserved.
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
DATA_DIR=../mnist_data
PYTHON=python
# run fl_mnist
bash run_mnist_local.sh ${DATA_DIR} ${PYTHON}
# run baseline
${PYTHON} baseline.py -d ${DATA_DIR}


grep loss logs/leader.log
