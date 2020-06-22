#!/bin/bash

CURRENT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

http_server_log_dir="${CURRENT_DIR}/http_server_logs"
data_join_log_dir="${CURRENT_DIR}/data_join_logs"
IFS='-' read -r -a array <<< "$RANK_UUID"
export INDEX="${array[1]}"

get_http_server_pid() {
    http_server_pid=`ps aux | grep "python $CURRENT_DIR/route_server.py" | grep -v grep | awk '{print $2}'`
    if [[ -n ${http_server_pid} ]]; then
        return 0
    else
        return 1
    fi
}

get_data_join_server_pid() {
    data_join_server_pid=`ps aux | grep "python $CURRENT_DIR/data_join/data_join_server.py" | grep -v grep | awk '{print $2}'`
    if [[ -n ${data_join_server_pid} ]]; then
        return 0
    else
        return 1
    fi
}

mkdir_http_server_log_dir() {
    if [[ ! -d $http_server_log_dir ]]; then
        mkdir -p $http_server_log_dir
    fi
}

mkdir_data_join_log_dir() {
    if [[ ! -d $data_join_log_dir ]]; then
        mkdir -p $data_join_log_dir
    fi
}

http_server_status() {
    get_http_server_pid
    if [[ -n ${http_server_pid} ]]; then
        echo "http_server_status:
        `ps aux | grep ${http_server_pid} | grep -v grep`"
        exit 1
    else
        echo "http service not running"
        exit 0
    fi
}

data_join_server_status() {
    get_data_join_server_pid
    if [[ -n ${data_join_server_pid} ]]; then
        echo "data_join_server_pid:
        `ps aux | grep ${data_join_server_pid} | grep -v grep`"
        exit 1
    else
        echo "data join service not running"
        exit 0
    fi
}

start_http_server() {
    get_http_server_pid
    if [[ $? -eq 1 ]]; then
        mkdir_http_server_log_dir
        nohup python $CURRENT_DIR/route_server.py >> "${http_server_log_dir}/console.log" 2>>"${http_server_log_dir}/error.log" &
        if [[ $? -eq 0 ]]; then
            sleep 2
            get_http_server_pid
            if [[ $? -eq 0 ]]; then
                echo "http service start successful. pid: ${http_server_pid}"
            else
                echo " http service start failed"
            fi
        else
            echo "http service start failed"
        fi
    else
        echo "http service already started. pid: ${http_server_pid}"
    fi
}


data_join_server_start() {
    get_data_join_server_pid
    if [[ $? -eq 1 ]]; then
        mkdir_data_join_log_dir
        python $CURRENT_DIR/data_join/data_join_server.py $REMOTE_IP $INDEX $PARTITION_ID $DATA_SOURCE_NAME $DATA_BLOCK_DIR $RAW_DATA_DIR $ROLE -m=$MODE -p=$PORT0 --raw_data_iter=$RAW_DATA_ITER --compressed_type=$COMPRESSED_TYPE --example_joiner=$EXAMPLE_JOINER $EAGER_MODE
        if [[ $? -eq 0 ]]; then
            sleep 2
            get_data_join_server_pid
            if [[ $? -eq 0 ]]; then
                echo "data join service start successfully. pid: ${data_join_server_pid}"
            else
                echo " data join service start failed"
            fi
        else
            echo "data join service start failed"
        fi
    else
        echo "data join service already started. pid: ${http_server_pid}"
    fi
}


case "$1" in
    start)
        start_http_server
        data_join_server_start
        http_server_status
        data_join_server_status
        ;;
    *)
        echo "usage: $0 {start|http_server_status|data_join_server_status}"
        exit -1
esac
