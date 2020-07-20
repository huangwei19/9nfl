### FL Mnist Demo
#### Prerequisite
1. Generate mnist data for fl. See `example/mnist_data`.
2. Put `fl_comm_libs` in this directory .
```
cp -r ../../src/Trainer/fl_comm_libs .
```

#### Standalone Mode
1. Prepare python3 environment

We recommand to use virtualenv to get rid of environment problems. 
Use `pip install virtualenv` to install virtualenv.

```bash
cd ~
# create an python environment
virtualenv fl-env
# activate it
source fl-env/bin/activate

# install tensorflow 1.15 and protobuf 3.8.0
pip install -r requirements.txt

# fix the tensorflow for fl tasks
wget https://github.com/tensorflow/tensorflow/blob/r1.15/tensorflow/python/pywrap_dlopen_global_flags.py 
cp pywrap_dlopen_global_flags.py fl-env/lib/python3.6/site-packages/tensorflow_core/python/

```

If you choose not to use virtualenv, make sure you install tensorflow 1.15 and protobuf 3.8.0. Then, download [pywrap_dlopen_global_flags.py](https://github.com/tensorflow/tensorflow/blob/r1.15/tensorflow/python/pywrap_dlopen_global_flags.py) and copy it into your python tensorflow dir e.g. `site-packages/tensorflow_core/python/`.

2. run `fl_mnist`
```bash
DATA_DIR=../mnist_data
PYTHON=python

# run fl_mnist
bash run_mnist_local.sh ${DATA_DIR} ${PYTHON}

# run baseline
${PYTHON} baseline.py -d ${DATA_DIR}
```

2. compare loss
```bash
# get loss by fl
grep loss logs/leader.log
```




