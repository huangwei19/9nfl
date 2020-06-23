### FL Mnist Demo
#### Prerequisite
1. Generate mnist data for fl. See `example/mnist_data`.
2. Put `fl_comm_libs` in this directory .

#### Standalone Mode
```bash
DATA_DIR=../mnist_data
PYTHON=python

# run fl_mnist
bash run_mnist_local.sh ${DATA_DIR} ${PYTHON}

# run baseline
${PYTHON} baseline.py -d ${DATA_DIR}

# compare loss
grep loss logs/leader.log
```


