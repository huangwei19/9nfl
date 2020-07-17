### FL Mnist Demo
#### Prerequisite
1. Generate mnist data for fl. See `example/mnist_data`.
2. Put `fl_comm_libs` in this directory .
```
cp -r ../../src/Trainer/fl_comm_libs .
```

#### Standalone Mode
1. run `fl_mnist`
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




