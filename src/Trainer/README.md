### FL Trainer
You can choose to use our prebuild `_fl_ops.so` or compile `_fl_ops.so` from source code by yourself.

#### Prerequisite for compiling
1. Tensorflow 1.15 source code
```bash
git clone https://github.com/tensorflow/tensorflow.git
git chekout -b r1.15 origin/r1.15
```
2. bazel 0.26.1
refer [bazel github](https://github.com/bazelbuild/bazel/releases/tag/0.26.1)
```bash
wget https://github.com/bazelbuild/bazel/releases/download/0.26.1/bazel-0.26.1-installer-linux-x86_64.sh
sh bazel-0.26.1-installer-linux-x86_64.sh --user
```
3. GCC 5.2

#### Compile
```bash
bash compile.sh ${full_path_of_your_tensorflow_dir}
```
