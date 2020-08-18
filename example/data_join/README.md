数据求交示例
--------
### 前提
准备好要求交的数据, 参见[mnist_data](../mnist_data/README.md)

### 单机版
环境准备参见[数据求交单机版安装指导](install/DataJoin/simpleness_install_chinese_version.md)

启动数据求交的leader和follower
```bash 
bash data_join_leader.sh
bash data_join_follower.sh
```
求交需要花费一些时间, 日志在`src/DataJoin/logs/data_join_logs`, 输出结果在`../mnist_data/data_block_leader`和`../mnist_data/data_block_follower`


