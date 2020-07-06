[doc]
一. Stand-alone Deployment Guide:

1. DownLoad 
Download package from git address https://git.jd.com/ads-conversion/9nfl_opensource.git
`git clone https://git.jd.com/ads-conversion/9nfl_opensource.git`
   
2. Set Environment
copy or move 9nfl_opensource into /app (you can change the root dir /app into yours directory);
if root dir /app does not exists,please mkdir /app
`copy -r 9nfl_opensource /app`
`su root`

if python3.6 is installed by anaconda3
`echo "/app/9nfl_opensource/src" > /usr/local/lib64/python3.6/site-packages/tmp.pth`
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
export REMOTE_IP="10.170.95.39:5001"
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
export REMOTE_IP="10.170.95.39:6001"
export RANK_UUID=DataJoinWorker-0
export RAW_DATA_ITER=TF_RECORD_ITERATOR
export EXAMPLE_JOINER=MEMORY_JOINER

`cd /app/9nfl_opensource/src/DataJoin/`
`sh start_server join`


二. Cluster Deployment Guide:

1. Make Base Image

`cd /app/9nfl_opensource/deploy/data_join/images` 

`docker build -t  FROM mirror.jd.com/pino/fl/opensource_tf1.15_base:v0.1 . -f Base_Dockerfile`

please replace "mirror.jd.com/pino/fl/opensource_tf1.15_base:v0.1"  with your base image name 

2. Make  Data Join Image

`cd /app/9nfl_opensource/deploy/data_join/images`

`docker build -t  mirror.jd.com/pino/fl:data_join_leader_opensource_v1.0 . -f Base_Dockerfile`

please replace "mirror.jd.com/pino/fl:data_join_leader_opensource_v1.0"  with your data join image name 

Making leader data join image  and follower data join image is the same  as the second step

3. deploy

`cd /app/9nfl_opensource/deploy/data_join/k8s`

After finished setting Environment variables, and replace the Environment variables of 
the deployment_worker.yaml with real value;

`deployment_worker.yaml | kubectl --namespace=${NAMESPACE} create -f -`





 
 







    