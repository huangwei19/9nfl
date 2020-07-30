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
WORK_DIR=$(cd `dirname $0`;pwd)
MNIST_DIR=`readlink -f "${WORK_DIR}"`

DATA_DIR=$1
PYTHON=$2

if [ -z ${DATA_DIR} ];then
    DATA_DIR='../mnist_data'
fi

if [ -z $PYTHON ];then
    PYTHON=python
fi

local_host="`hostname --fqdn`"
LOCAL_IP=`/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`

CHECK_EXAMPLEID=1
DATA_MODE="local"

L_TRAIN="${DATA_DIR}/leader_train"
F_TRAIN="${DATA_DIR}/follower_train"
L_TEST="${DATA_DIR}/leader_test"
F_TEST="${DATA_DIR}/follower_test"


L_DC_ADDR="${LOCAL_IP}:40003"
F_DC_ADDR="${LOCAL_IP}:40005"

L_TRAIN_ADDR="${LOCAL_IP}:40001"
F_TRAIN_ADDR="${LOCAL_IP}:40002"

if [ ! -d ${MNIST_DIR}/logs ];then
    mkdir ${MNIST_DIR}/logs
fi

export  _FILE_GET_CMD="./local_get.sh"

train(){
set -x
$PYTHON ${MNIST_DIR}/dc_leader.py -p ${L_TRAIN} -m ${DATA_MODE}> ${MNIST_DIR}/logs/dc_leader.log 2>&1 &
$PYTHON ${MNIST_DIR}/dc_follower.py -p ${F_TRAIN} -m ${DATA_MODE}> ${MNIST_DIR}/logs/dc_follower.log 2>&1 &

$PYTHON  ${MNIST_DIR}/mnist_leader.py --local_addr="${L_TRAIN_ADDR}" \
--peer_addr="${F_TRAIN_ADDR}" --dc_addr="${L_DC_ADDR}" \
--rpc_service_type=1 \
--local_debug=1 \
--check_exampleid=$CHECK_EXAMPLEID \
--model_dir="./models/leader_model" \
--export_dir="./models/leader_export_savemodel" \
> ${MNIST_DIR}/logs/leader.log 2>&1 &

$PYTHON  ${MNIST_DIR}/mnist_follower.py --local_addr="${F_TRAIN_ADDR}" \
--peer_addr="${L_TRAIN_ADDR}" --dc_addr="${F_DC_ADDR}" \
--rpc_service_type=1 \
--local_debug=1 \
--check_exampleid=$CHECK_EXAMPLEID \
--model_dir="./models/follower_model" \
--export_dir="./models/follower_export_savemodel" \
> ${MNIST_DIR}/logs/follower.log 2>&1 &

}

rm -rf models/*
bash kill.sh
train


