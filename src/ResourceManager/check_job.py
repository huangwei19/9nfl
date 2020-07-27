# coding=utf-8
"""python script for check task status on Kubernetes"""
import sys
import argparse
import json
from commands import getstatusoutput as sys_execute

def get_args():
    """get command arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("role", help="is leader or follower")
    parser.add_argument("task_id", help="the task id to check")
    return parser.parse_args()

def check():
    """check status"""
    args = get_args()
    name_space = 'fl-follower'
    if args.role == '1':
        name_space = 'fl-leader'
    retcode = {'Running':0, 'Created':0, 'Restarting':0, 'Succeeded':1, 'Failed':2}
    try:
        status, output = sys_execute('kubectl get tfjob -l instanceId=%s -n %s -o json' \
        % (args.task_id, name_space))
        if status != 0:
            print 'Error: %s' % output
            sys.exit(3)
        json_dt = json.loads(output)
        sys.exit(retcode[json_dt['items'][0]['status']['conditions'][-1]['type']])
    except Exception as e_str:
        print 'Exception: %s' % str(e_str)
        sys.exit(3)

if __name__ == '__main__':
    check()
