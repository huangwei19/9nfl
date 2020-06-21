#!/bin/bash

CURRENT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHONPATH=$PYTHONPATH:CURRENT_DIR/../..:CURRENT_DIR/common/protobuf:/opt/tiger/pyutil
log_dir="${CURRENT_DIR}/logs"
IFS='-' read -r -a array <<< "$WORKER_UUID"
export INDEX="${array[1]}"

get_pid() {
    pid=`ps aux | grep "python route_server" | grep -v grep | awk '{print $2}'`
    if [[ -n ${pid} ]]; then
        return 0
    else
        return 1
    fi
}

mkdir_logs_dir() {
    if [[ ! -d $log_dir ]]; then
        mkdir -p $log_dir
    fi
}

status() {
    get_pid
    if [[ -n ${pid} ]]; then
        echo "status:
        `ps aux | grep ${pid} | grep -v grep`"
        exit 1
    else
        echo "service not running"
        exit 0
    fi
}

start() {
    get_pid
    if [[ $? -eq 1 ]]; then
        mkdir_logs_dir
        nohup python $CURRENT_DIR/route_server.py >> "${log_dir}/console.log" 2>>"${log_dir}/error.log" &
        python $CURRENT_DIR/data_join/data_join_worker.py $REMOTE_IP $INDEX $PARTITION_ID $DATA_SOURCE_NAME $DATA_BLOCK_DIR $RAW_DATA_DIR $ROLE -m=$MODE -p=$PORT0 --raw_data_iter=$RAW_DATA_ITER --compressed_type=$COMPRESSED_TYPE --example_joiner=$EXAMPLE_JOINER $EAGER_MODE
        if [[ $? -eq 0 ]]; then
            sleep 2
            get_pid
            if [[ $? -eq 0 ]]; then
                echo "service start sucessfully. pid: ${pid}"
            else
                echo "service start failed"
            fi
        else
            echo "service start failed"
        fi
    else
        echo "service already started. pid: ${pid}"
    fi
}

stop() {
    get_pid
    if [[ -n ${pid} ]]; then
        echo "killing:
        `ps aux | grep ${pid} | grep -v grep`"
        kill -9 ${pid}
        if [[ $? -eq 0 ]]; then
            echo "killed"
        else
            echo "kill error"
        fi
    else
        echo "service not running"
    fi
}


case "$1" in
    start)
        start
        status
        ;;

    stop)
        stop
        ;;
    status)
        status
        ;;

    restart)
        stop
        start
        status
        ;;
    *)
        echo "usage: $0 {start|stop|status}"
        exit -1
esac
