#!/bin/sh
#Copyright: JD.com (2014)
CUR_PATH=`pwd`
PROJECT_PATH=`dirname $CUR_PATH`
OPT="-j 8 --copt -DHAVE_ZLIB=1 --copt=-g --copt=-Wno-comment --copt=-DRAPIDJSON_HAS_STDSTRING --define with_glog=true"
function execshell()
{
    echo "[execshell]$@ begin."
    eval $@
    [[ $? != 0 ]] && {
        echo "[execshell]$@ failed."
        exit 1
    }
    echo "[execshell]$@ success."
    return 0
}
function build_common()
{
    rm -rf output*
    mode=${1:-"opt"}
    execshell "bazel build server/... ${OPT} -c ${mode}"

    # 输出到output文件夹
    bin="./output/bin"
    if [[ ! -d ${bin} ]]
    then
        execshell "mkdir -p ${bin}"
    fi
    src_path="./bazel-bin"
    for src_com in \
        "server/fl_server" "server/fl_client"
    do
        execshell "cp $src_path/$src_com ${bin}"
    done

    # 生成commit id
    commit_id_file=commit_id.txt
    execshell "echo commit_id `git rev-parse HEAD` > $commit_id_file"
}

function build_clean()
{
    execshell "bazel clean"
}

function build_release()
{
    build_common "opt"
}

function build_debug()
{
    build_common "dbg"
}

function usage()
{
    cat <<HELP_END
用法：sh build.sh [参数]
        clean                       清理当前编译环境和xts运行环境
        debug                       编译debug版本
        release或缺省               编译release版本
        --help                      显示帮助信息
HELP_END
}
case $1 in
    clean)
        execshell "build_clean"
    ;;
    release|'')
        execshell "build_clean"
        execshell "build_release"
    ;;
    debug)
        execshell "build_clean"
        execshell "build_debug"
    ;;
    --help|-h|-help|help|*)
        usage
    ;;
esac
exit 0
