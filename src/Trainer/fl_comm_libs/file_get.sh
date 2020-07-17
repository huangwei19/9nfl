#!/bin/bash
DFS_FILE=$1
DEST_FILE=$2

if [ "$#" -ne 2 ]; then
    echo "You must provide exactly 2 arguments"
    exit 3
fi

DEST_DIR=`dirname ${DEST_FILE}`

let retries=0

while [ 0 -eq 0 ]
do
    echo "[HDFS INFO] >> Get File Start "

    if [ ! -e "${DEST_DIR}" ];then
        echo ${DEST_DIR} "not exist create"
        mkdir -p "${DEST_DIR}"
    fi

    if [ -f "${DEST_FILE}" ];then
        echo "${DEST_FILE} Exists! Remove it First."
        \rm -f "${DEST_FILE}"
    fi
    hadoop fs -get "${DFS_FILE}" "${DEST_FILE}"
    #filename=`basename ${DFS_FILE}`

    # check and retry
    if [ $? -eq 0 ]; then
        echo "[HDFS INFO] >> Get File ${DFS_FILE} complete "
        break;
    else
        ((retries++))
        if [[ ${retries} -gt 10 ]]; then
           exit 1
        fi
        echo "[HDFS ERROR] >> Get File ${DFS_FILE} ERROR Occur, retry in 2 seconds"
        sleep 2
    fi
done

exit 0
