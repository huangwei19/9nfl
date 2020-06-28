# Deploy Fedlearner
## On Kubernetes
京东联邦学习系统支持部署在k8s集群中，并利用[KubeFlow](https://www.kubeflow.org/)中的[tf-operator](https://github.com/kubeflow/tf-operator)进行训练集群搭建、管理、状态监控。
### 安装Kubernetes集群
如果你已经有了自己的k8s集群，则调过该步骤。
你可以选择搭建自己一套k8s集群或者搭建一套[MiniKube](https://kubernetes.io/docs/tasks/tools/install-minikube/)以快速验证。集群搭建完成后，请保证coordinator环境中的kubectl能够正常访问你搭建的k8s集群。
### 安装KubeFlow
按照[KubeFlow安装](https://www.kubeflow.org/docs/started/getting-started/)部署KubeFlow，目前我们测试的版本为v0.4。如果需要安装更高版本，则对应修改适配`src/ResourceManager/template`中的[任务模板](https://git.jd.com/ads-conversion/9nfl_opensource/tree/resource_manager/src/ResourceManager/template)即可。
### 共享存储
京东联邦学习系统分布式训练模式依赖共享文件系统保持训练中的数据目录以及模型目录的数据同步，但不限制具体的共享文件系统的架构和版本。具体使用看[这里](https://git.jd.com/ads-conversion/9nfl_opensource/tree/resource_manager/conf/ResourceManager)。
## coordinator
### k8s
coordinator会将联邦学习任务部署在k8s集群中，所以请保证k8s集群已经处于可用状态，kubectl配置正确，能够正常访问自己的k8s集群。
另外coordinator依赖python2以及jinja2用于将任务部署在k8s集群中。jinja2安装方法：
`pip install Jinja2==2.11.2`