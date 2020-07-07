# Deploy Fedlearner
## On Kubernetes
京东联邦学习系统支持部署在k8s集群中，并利用[KubeFlow](https://www.kubeflow.org/)中的[tf-operator](https://github.com/kubeflow/tf-operator)进行训练集群搭建、管理、状态监控。
### 安装Kubernetes集群
如果你已经有了自己的k8s集群，则调过该步骤。
你可以选择搭建自己一套k8s集群或者搭建一套[MiniKube](https://kubernetes.io/docs/tasks/tools/install-minikube/)以快速验证。集群搭建完成后，请保证coordinator环境中的kubectl能够正常访问你搭建的k8s集群。
### 安装KubeFlow
按照[KubeFlow安装](https://www.kubeflow.org/docs/started/getting-started/)部署KubeFlow，目前我们测试的版本为v0.4。如果需要安装更高版本，则对应修改适配`src/ResourceManager/template`中的[任务模板](https://git.jd.com/ads-conversion/9nfl_opensource/tree/resource_manager/src/ResourceManager/template)即可。
### hdfs
京东联邦学习系统以来hdfs来保存checkpoint和最终导出模型，所以训练镜像中请确保有hdfs环境，并且参考[TensorFlow on Hadoop](https://github.com/tensorflow/examples/blob/master/community/en/docs/deploy/hadoop.md)确保TensorFlow能够访问你的hdfs。然后可以在[配置](https://git.jd.com/ads-conversion/9nfl_opensource/tree/resource_manager/conf/ResourceManager)中配置相关hdfs路径。
## coordinator
### k8s
coordinator会将联邦学习任务部署在k8s集群中，所以请保证k8s集群已经处于可用状态，kubectl配置正确，能够正常访问自己的k8s集群。
另外coordinator依赖python2以及jinja2用于将任务部署在k8s集群中。jinja2安装方法：
`pip install Jinja2==2.11.2`