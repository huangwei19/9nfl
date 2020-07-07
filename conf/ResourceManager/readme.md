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
+ save
京东联邦学习使用hdfs来保存模型。本模块用于配置两侧模型的checkpoint以及模型保存路径。
其中{leader/follower}_model_dir用于保存checkpoint。{leader/follower}_export_dir用于最终导出模型。四个目录不能为相同目录。