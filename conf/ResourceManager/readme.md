# K8S conf for deploy Fedlearner
k8s.conf用于将京东联邦学习系统部署在kubernetes集群中。京东联邦学习分为leader以及leader两侧，两侧的k8s.conf应不相同。
配置文件分为4个模块：
+ coordinator
配置为对应侧的coordinator的Ip以及Port。
+ proxy
配置为对应侧的proxy的Ip以及Port。
+ image
用于配置DataCenter以及Trainer模块的镜像。
+ train
用于配置训练器的启动命令。
+ share_volume
京东联邦学习分布式训练中需要数据以及模型多容器共享，故依赖共享存储。本模块用于配置两侧数据与模块的网盘共享路径。
其中data_dir会映射到训练容器中的/workspace/data;models_dir会映射到训练容器中的/workspace/models。