# Deploy Fedlearner
## On Kubernetes
The JD federal learning system supports deployment in the k8s cluster, and uses the [tf-operator](https://github.com/kubeflow/tf-operator)in [KubeFlow](https://www.kubeflow.org/) to build, manage, and monitor the training cluster.
### Install Kubernetes
If you already have your own k8s cluster, skip this step.
You can choose to build your own k8s cluster or build a [MiniKube](https://kubernetes.io/docs/tasks/tools/install-minikube/) for quick verification. After the cluster is built, please ensure that kubectl in the coordinator environment can access the k8s cluster.
### Install KubeFlow
Deploy KubeFlow according to the [tutorial](https://www.kubeflow.org/docs/started/getting-started/), the version we tested is currently v0.4. If you need to install a higher version, you can modify the task template in `src/ResourceManager/template`.
### HDFS
The JD Federal Learning System relies on hdfs to save checkpoints and export models, so please ensure that you have an hdfs environment in the training image, and refer to [TensorFlow on Hadoop](https://github.com/tensorflow/examples/blob/master/community/en/docs/deploy/hadoop.md) to ensure that TensorFlow can access your hdfs. Then you can configure the relevant hdfs path in the [configuration](https://git.jd.com/ads-conversion/9nfl_opensource/tree/resource_manager/conf/ResourceManager)).
## coordinator
### k8s
The coordinator will deploy the JD federal learning tasks in the k8s cluster, so please ensure that the k8s cluster is already available, kubectl is configured correctly, and can access your k8s cluster.
In addition, the coordinator relies on python2 and jinja2 for deploying tasks in the k8s cluster. Jinja2 installation:
`pip install Jinja2==2.11.2`