#!/bin/bash

kill -9 `ps -aux | grep python | grep leader | awk '{print $2}'`
kill -9 `ps -aux | grep python | grep follower | awk '{print $2}'`
kill -9 `ps -aux | grep python | grep dc_leader | awk '{print $2}'`
kill -9 `ps -aux | grep python | grep dc_follower | awk '{print $2}'`
kill -9 `ps -aux | grep python | grep co_proxy_server | awk '{print $2}'`
kill -9 `ps -aux | grep python | grep peer_debug | awk '{print $2}'`


