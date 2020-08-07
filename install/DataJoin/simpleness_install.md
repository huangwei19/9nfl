[doc]
一. Stand-alone Deployment Guide:

1. DownLoad 
Download package from open_source git address :xxx
`git clone xxx`
#please replace xxx with open source git address
   
2. Set Environment
copy or move 9nfl_opensource into /app (you can change the root dir /app into yours directory);
if root dir /app does not exists,please mkdir /app
`copy -r 9nfl_opensource /app`
`su root`

if python3.6 is installed by anaconda3
`echo "/app/9nfl_opensource/src" >  /usr/local/anaconda3/lib/python3.6/site-packages/tmp.pth`
if python3.6 is not installed  by anaconda3
`echo "/app/9nfl_opensource/src" > /usr/local/lib64/python3.6/site-packages/tmp.pth` 

please change user role from root into your current user role ,for example:
 `su ads_9ncloud`
 
 
3. Install Requirements
`cd /app/9nfl_opensource/src/DataJoin/`
`pip install -r requirements.txt`

4. make build

`copy -r /app/9nfl_opensource/protocols /app/9nfl_opensource/src/`

`cd /app/9nfl_opensource/src/`

`python -m grpc_tools.protoc -I protocols -Ithirdparty/tensorflow \
        --python_out=. \
        --grpc_python_out=. \
        protocols/DataJoin/common/*.proto`

5. Set Leader Environment

for example:
export ROLE=leader
export PARTITION_ID=0
export DATA_SOURCE_NAME=test_data_join
export MODE=local
export RAW_DATA_DIR=/app/9nfl_opensource/src/DataJoin/leader_train
export DATA_BLOCK_DIR=/app/9nfl_opensource/src/DataJoin/data_block_leader
export PORT0="6001"
export REMOTE_IP="follower_ip:5001"
#please replace follower_ip with follower server ip address
export RANK_UUID=DataJoinWorker-0
export RAW_DATA_ITER=TF_RECORD_ITERATOR
export EXAMPLE_JOINER=MEMORY_JOINER

`cd /app/9nfl_opensource/src/DataJoin/`
`sh start_server join`

6. Set Follower Environment

export ROLE=follower
export PARTITION_ID=0
export DATA_SOURCE_NAME=test_data_join
export MODE=local
export RAW_DATA_DIR=/app/9nfl_opensource/src/DataJoin/follower_train
export DATA_BLOCK_DIR=/app/9nfl_opensource/src/DataJoin/data_block_follower
export PORT0="5001"
export REMOTE_IP="leader_ip:6001"
#please replace leader_ip with leader server ip address
export RANK_UUID=DataJoinWorker-0
export RAW_DATA_ITER=TF_RECORD_ITERATOR
export EXAMPLE_JOINER=MEMORY_JOINER

`cd /app/9nfl_opensource/src/DataJoin/`
`sh start_server join`


