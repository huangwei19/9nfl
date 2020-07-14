#!/bin/bash
DFS_FILE=$1
DEST_FILE=$2

DEST_DIR=`dirname ${DEST_FILE}`

while [ 0 -eq 0 ]
do
    echo "[LOCAL INFO] >> Get File ${DFS_FILE} Start "

    if [ ! -e ${DEST_DIR} ];then
        echo ${DEST_DIR} "not exist create"
        mkdir -p ${DEST_DIR}
    fi
    if [ -f ${DEST_FILE} ];then
        echo "${DEST_FILE} Exists! Remove it First."
        \rm -f ${DEST_FILE}
    fi
    cp ${DFS_FILE} ${DEST_FILE}

    # check and retry

    if [ $? -eq 0 ]; then
        echo "[LOCAL INFO] >> Get File ${DFS_FILE} complete "
        break;
    else
        echo "[LOCAL ERROR] >> Get File ${DFS_FILE} ERROR Occur, retry in 2 seconds"
        echo ${DFS_FILE} >> HDFS_MISSING_FILE
        sort HDFS_MISSING_FILE -o HDFS_MISSING_FILE_TEMP
        uniq HDFS_MISSING_FILE_TEMP HDFS_MISSING_FILE
        sleep 2
    fi
done

exit 0

