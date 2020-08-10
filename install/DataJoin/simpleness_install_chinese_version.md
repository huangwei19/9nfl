[doc]
一. 单机版安装指导:

1. 下载
从开源地址下载源码
`git clone xxx`
# xxx替换成开源git开源地址
   
2. 设置环境变量
把开源代码主目录 9nfl_opensource 拷贝到 /app 下(你可以把/app替换成你自己的根目录文件夹);
如果根目录文件夹 /app不存在，需要执行命令：mkdir /app
`copy -r 9nfl_opensource /app`

切换当前用户到root权限：
`su root`

如果你的python3.6是通过anaconda安装的，执行下面的命令设置临时环境变量：
`echo "/app/9nfl_opensource/src" >  /usr/local/anaconda3/lib/python3.6/site-packages/tmp.pth`

否则执行以下命令设置临时环境变量：
`echo "/app/9nfl_opensource/src" > /usr/local/lib64/python3.6/site-packages/tmp.pth` 

设置完临时环境变量以后，切换为当前用户权限，例如:
 `su ads_9ncloud`
 #ads_9ncloud需要替换成你得当前用户权限
 
 
3. 安装相关依赖包

`cd /app/9nfl_opensource/src/DataJoin/`
`pip install -r requirements.txt`

4. 编译

拷贝protobuf文件到/app/9nfl_opensource/src/目录下：

`copy -r /app/9nfl_opensource/protocols /app/9nfl_opensource/src/`

下载tensorflow源码，并把tensorflow源码拷贝到/app/9nfl_opensource/src/thirdparty/tensorflow目录下

拷贝完以后，切换到/app/9nfl_opensource/src目录下：
`cd /app/9nfl_opensource/src`

在当前目录下，执行以下命令编译protobuf文件：
`python -m grpc_tools.protoc -I protocols -Ithirdparty/tensorflow --python_out=. --grpc_python_out=. protocols/DataJoin/common/*.proto`

5. Leader侧设置环境变量

在一台机器开两个终端，一端为leader侧，一端为follower侧
在leader侧设置环境变量：
export ROLE=leader
export PARTITION_ID=0
export DATA_SOURCE_NAME=test_data_join
export MODE=local
export RAW_DATA_DIR=/app/9nfl_opensource/src/DataJoin/leader_train
#数据求交的原始目录，替换成你自己的目录
export DATA_BLOCK_DIR=/app/9nfl_opensource/src/DataJoin/data_block_leader
#数据求交结果存放的额目录，替换成你自己的目录
export PORT0="6001"
export REMOTE_IP="follower_ip:5001"
#follower_ip替换为follower侧服务的ip，5001为follower侧得服务端口，可自己定义，
#需要与follower侧环境变量端口保持一致
export RANK_UUID=DataJoinWorker-0
export RAW_DATA_ITER=TF_RECORD_ITERATOR
export EXAMPLE_JOINER=MEMORY_JOINER

启动leader侧服务：
`cd /app/9nfl_opensource/src/DataJoin/`
`sh start_server join`

6. Follower侧设置环境变量

在follower侧设置环境变量：
export ROLE=follower
export PARTITION_ID=0
export DATA_SOURCE_NAME=test_data_join
export MODE=local
export RAW_DATA_DIR=/app/9nfl_opensource/src/DataJoin/follower_train
#数据求交的原始目录，替换成你自己的目录
export DATA_BLOCK_DIR=/app/9nfl_opensource/src/DataJoin/data_block_follower
#数据求交结果存放的额目录，替换成你自己的目录
export PORT0="5001"
export REMOTE_IP="leader_ip:6001"
#leader_ip替换为leader侧服务的ip，6001为leader侧得服务端口，可自己定义
#需要与leader侧环境变量端口保持一致
export RANK_UUID=DataJoinWorker-0
export RAW_DATA_ITER=TF_RECORD_ITERATOR
export EXAMPLE_JOINER=MEMORY_JOINER

启动follower侧服务：
`cd /app/9nfl_opensource/src/DataJoin/`
`sh start_server join`


