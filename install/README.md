# simpleness 
## Generate test data for FL
```Bash
cd 9nfl_opensource/example/mnist_data
```
Here is a instruction for you to do data processing.
## Trainer part preparation
```Bash
cd 9nfl_opensource/src/Trainer
```
You can choose to use our prebuild `_fl_ops.so` or compile `_fl_ops.so` from source code by yourself. The detail shows in readme.
## Trainer part verification
```Bash
cd 9nfl_opensource/example/mnist_demo
```
Here is FL Mnist Demo for the Trainer part verification.
## DataJoin part preparation
```Bash
cd 9nfl_opensource/install/DataJoin
```
Here is a simpleness_install.md to help you with DataJoin arrangement. When set leader environment (follower should be modified accordingly), here is a example setting instruction for you:
```Bash
export ROLE=leader
export PARTITION_ID=0
export DATA_SOURCE_NAME=test_data_join
export MODE=local
export RAW_DATA_DIR=/app/9nfl_opensource/src/DataJoin/leader_train                \\source data path
export DATA_BLOCK_DIR=/app/9nfl_opensource/src/DataJoin/data_block_leader         \\output path
export PORT0="6001"                                                               \\port of follower
export REMOTE_IP="10.170.95.39:5001"                                              \\ip should be the same as the follower in simpliness arrangement
export RANK_UUID=DataJoinWorker-0
export RAW_DATA_ITER=TF_RECORD_ITERATOR
export EXAMPLE_JOINER=MEMORY_JOINER
```
## DataCenter part preparation
```Bash
cd 9nfl_opensource/install/DataCenter
```
Here is a simpleness_install.md to help you with DataCenter arrangement. When set leader environment (follower is the same)
```Bash
export LEADER_DATA_BLOCK_DIR=/app/9nfl_opensource/src/DataJoin/data_block_leader      \\leader data path
export FOLLOWER_DATA_BLOCK_DIR=/app/9nfl_opensource/src/DataJoin/data_block_follower  \\follower data path
export DATA_NUM_EPOCH=1
export MODE=local
```

# distributer

