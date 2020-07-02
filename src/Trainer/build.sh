set -x

copy_file(){

    TENSORFLOW=$1
    JDFL=${TENSORFLOW}/tensorflow/contrib/jdfl
    mkdir ${JDFL}
    cp BUILD ${JDFL}
    cp -r kernels ${JDFL}
    cp -r ops ${JDFL}
    cp -r rpc ${JDFL}

    cp build/flops_build_.sh ${TENSORFLOW}/
    cp build/9nfl_build.patch ${TENSORFLOW}/tensorflow/
    cd ${TENSORFLOW}/tensorflow
    patch -p1 <9nfl_build.patch 
    cd -
}


TENSORFLOW=/export/huangwei19/proj/tensorflow
copy_file ${TENSORFLOW}
cd ${TENSORFLOW}
bash flops_build_.sh


#~/anaconda3/bin/python setup.py sdist
