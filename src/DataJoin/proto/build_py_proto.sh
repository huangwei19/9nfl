#!/usr/bin/env bash

BASEDIR=$(dirname "$0")/..
cd $BASEDIR



python -m grpc_tools.protoc -I../fate_flow/proto/protocols/ --python_out=../fate_flow/proto/protoapi --grpc_python_out=../fate_flow/proto/protoapi data-intersection-master.proto

python -m grpc_tools.protoc -I../fate_flow/proto/protocols/ --python_out=../fate_flow/proto/protoapi --grpc_python_out=../fate_flow/proto/protoapi data-intersection-leader.proto

python -m grpc_tools.protoc -I../fate_flow/proto/protocols/ --python_out=../fate_flow/proto/protoapi --grpc_python_out=../fate_flow/proto/protoapi data-intersection-follower.proto






