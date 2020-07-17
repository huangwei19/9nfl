
copy_file(){

    TENSORFLOW=$1
    JDFL=${TENSORFLOW}/tensorflow/contrib/jdfl
    mkdir ${JDFL}
    cp BUILD ${JDFL}
    cp -r kernels ${JDFL}
    cp -r ops ${JDFL}
    cp -r rpc ${JDFL}

    cp build/flops_build.sh ${TENSORFLOW}/
}


TENSORFLOW=$1
if [ -z ${TENSORFLOW} ];then
    echo "usage: bash $0 tensorflow_dir"
    exit -1
fi

set -x
copy_file ${TENSORFLOW}
cd ${TENSORFLOW}
bash flops_build.sh
cd -
cp ${TENSORFLOW}/bazel-bin/tensorflow/contrib/jdfl/_fl_ops.so .


#~/anaconda3/bin/python setup.py sdist
