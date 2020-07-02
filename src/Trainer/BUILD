# Description:
# An example for custom op and kernel defined as a TensorFlow plugin.

package(
    default_visibility = ["//tensorflow:internal"],
)

licenses(["notice"])  # Apache 2.0

exports_files(["LICENSE"])

load("//tensorflow:tensorflow.bzl", "tf_custom_op_library")
load("//tensorflow:tensorflow.bzl", "tf_py_test")
load("//tensorflow:tensorflow.bzl", "tf_cc_test")
load(
    "//tensorflow/core/platform:default/build_config.bzl",
    "tf_proto_library",
    "cc_proto_library",
    "tf_proto_library_cc",
    "tf_kernel_tests_linkstatic",
)

FL_INCS = [
]

COMMON_OPTS = [
    "-fexceptions",
] + FL_INCS

tf_proto_library(
    name = "jdfl_rpc_proto",
    srcs = [
        "rpc/proto/bridge_agent.proto",
        "rpc/proto/dc_agent.proto",
    ],
    protodeps = [ "//tensorflow/core:protos_all" ],
    cc_api_version = 2,
    has_services = 1,
    cc_grpc_version = 1,
    visibility = ["//visibility:public"],
)

cc_library(
    name = "jdfl_rpc_hdrs",
    hdrs = glob([
        "kernels/**/*.h",
        "ops/**/*.h",
        "rpc/**/*.h",
    ]),
)

tf_custom_op_library(
    name = "_fl_ops.so",
    srcs = glob([
        "kernels/**/*.cc",
        "ops/**/*.cc",
        "rpc/**/*.cc",
    ],
    exclude = [

    ]),
    deps = [
        ":jdfl_rpc_proto_cc",
        ":jdfl_rpc_hdrs",
        "//tensorflow/core:tf_core_inc",
        "//tensorflow/core/kernels/data:tf_name_utils_inc",
        "//tensorflow/core/distributed_runtime/rpc:tf_rpc_inc",
        "//tensorflow/core/distributed_runtime/rpc:async_service_interface",
        "//tensorflow/core/distributed_runtime:tf_call_options_inc",
        "@grpc//:grpc++",
    ],
    copts = COMMON_OPTS,
)


py_library(
    name = "all_proto_py",
    srcs_version = "PY2AND3",
    deps = [
        ":jdfl_rpc_proto_py",
    ],
)

filegroup(
    name = "all_files",
    srcs = glob(
        ["**/*"],
        exclude = [
            "**/METADATA",
            "**/OWNERS",
        ],
    ),
    visibility = ["//tensorflow:__subpackages__"],
)

