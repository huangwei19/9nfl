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
        
5. Execute Data Center Server

export LEADER_DATA_BLOCK_DIR=/app/9nfl_opensource/src/DataJoin/data_block_leader
export FOLLOWER_DATA_BLOCK_DIR=/app/9nfl_opensource/src/DataJoin/data_block_follower
export DATA_NUM_EPOCH=1
export MODE=local

`cd /app/9nfl_opensource/src/DataJoin`

`sh start_server.sh center`


二. Cluster Deployment Guide:

1. Make Data Center Image

`cd /app/9nfl_opensource/deploy/data_center/images`
`docker build -t  mirror.jd.com/pino/fl:data_center_leader_opensource_v1.0 . -f Data_Center_Dockerfile`

please replace "mirror.jd.com/pino/fl:data_center_leader_opensource_v1.0"  with your data join image name 

when Making follower data center image,need to change mysql config as follower mysql 
 the method of making is follower data center image is the same  as above

        

    