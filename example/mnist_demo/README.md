FL Mnist Demo
----------------
#### 先决条件
1. 准备好求交后的mnist数据, 供fl训练器使用,
   参见[mnist_data](../mnist_data/README.md)和[data_join](../data_join/README.md)

2. 运行单机版前，将`fl_comm_libs`复制到这个目录
```
cp -r ../../src/Trainer/fl_comm_libs .
```

#### 单机版
1. 准备python3环境

我们推荐使用`virtualenv`来避免python相关的环境问题

运行`pip install virtualenv`来安装virtualenv

```bash
cd ~
# create an python environment
virtualenv fl-env
# activate it
source fl-env/bin/activate

# 要求 tensorflow 1.15 和 protobuf 3.8.0
pip install -r requirements.txt

# 配置tensorflow
wget https://github.com/tensorflow/tensorflow/blob/r1.15/tensorflow/python/pywrap_dlopen_global_flags.py 
cp pywrap_dlopen_global_flags.py fl-env/lib/python3.6/site-packages/tensorflow_core/python/
```

如果不打算使用virutalenv, 请确保tensorflow版本为1.15且protobuf版本为3.8.0.
然后下载[pywrap_dlopen_global_flags.py](https://github.com/tensorflow/tensorflow/blob/r1.15/tensorflow/python/pywrap_dlopen_global_flags.py)并拷贝到tensorflow目录, 例如`site-packages/tensorflow_core/python/`

2. 运行mnist demo
我们提供了一个神经网络的例子来验证联邦学习框架的正确性:
一张mnist图片被分成两半，分别由leader和follower所有，leader和follower共同训练一个神经网络模型.
```
# 用联邦学习框架训练模型
bash run_mnist_local_leader.sh
bash run_mnist_local_follower.sh

# 用原生tensorflow训练模型
python baseline.py -d ${DATA_DIR}

```

3. 比较loss
配置相同情况下, 联邦学习模型loss的变化情况应与原生tensorflow框架的loss变化一致
```
# 联邦学习模型的loss变化情况
grep loss logs/leader.log
```
