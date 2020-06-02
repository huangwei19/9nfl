set -x
WORK_DIR=$(cd `dirname $0`;pwd)
MNIST_DIR=`readlink -f "${WORK_DIR}"`

DATA_DIR=$1
PYTHON=$2

if [ -z $PYTHON ];then
    PYTHON=python
fi

local_host="`hostname --fqdn`"
LOCAL_IP=`/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`

L_TRAIN="${DATA_DIR}/leader_train"
F_TRAIN="${DATA_DIR}/follower_train"
L_TEST="${DATA_DIR}/leader_test"
F_TEST="${DATA_DIR}/follower_test"


L_DC_ADDR="${LOCAL_IP}:40003"
F_DC_ADDR="${LOCAL_IP}:40005"

L_TRAIN_ADDR="${LOCAL_IP}:40001"
F_TRAIN_ADDR="${LOCAL_IP}:40002"

L_PROXY_ADDR=${F_TRAIN_ADDR}
F_PROXY_ADDR=${L_TRAIN_ADDR}

L_COORDINATOR_ADDR="${LOCAL_IP}:40004"
F_COORDINATOR_ADDR="${LOCAL_IP}:40004"


if [ ! -d ${MNIST_DIR}/log ];then
    mkdir ${MNIST_DIR}/log
fi

train(){
$PYTHON ${MNIST_DIR}/co_proxy_server.py > ${MNIST_DIR}/log/proxy.log 2>&1 &
$PYTHON ${MNIST_DIR}/dc_leader.py ${L_TRAIN} > ${MNIST_DIR}/log/dc_leader.log 2>&1 &
$PYTHON ${MNIST_DIR}/dc_follower.py ${F_TRAIN} > ${MNIST_DIR}/log/dc_follower.log 2>&1 &

$PYTHON  ${MNIST_DIR}/mnist_leader.py --local_addr="${L_TRAIN_ADDR}" \
--peer_addr="${F_TRAIN_ADDR}" --dc_addr="${L_DC_ADDR}" \
--coordinator_addr="${L_COORDINATOR_ADDR}" --proxy_addr="${L_PROXY_ADDR}" \
--rpc_service_type=1 \
> ${MNIST_DIR}/log/leader.log 2>&1 &

$PYTHON  ${MNIST_DIR}/mnist_follower.py --local_addr="${F_TRAIN_ADDR}" \
--peer_addr="${L_TRAIN_ADDR}" --dc_addr="${F_DC_ADDR}" \
--coordinator_addr="${F_COORDINATOR_ADDR}" --proxy_addr="${F_PROXY_ADDR}" \
--rpc_service_type=1 \
> ${MNIST_DIR}/log/follower.log 2>&1 &

}

bash kill.sh
train


