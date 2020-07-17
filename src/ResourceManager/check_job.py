# coding=utf-8
import os,sys
import argparse
import ConfigParser
import json
from commands import getstatusoutput as sys_execute

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("role", help="is leader or follower")
    parser.add_argument("task_id", help="the task id to check")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    if args.role == '1':
        ns = 'fl-leader'
    else:
        ns = 'fl-follower'
    retcode = {'Running':0,'Created':0,'Restarting':0,'Succeeded':1,'Failed':2}
    try:
        status,output = sys_execute('kubectl get tfjob -l instanceId=%s -n %s -o json' % (args.task_id,ns))
        if status != 0:
            print 'Error:', cmd, output
            sys.exit(3)
        dt = json.loads(output) 
        sys.exit(retcode[dt['items'][0]['status']['conditions'][-1]['type']])
    except Exception as e:
        sys.exit(3)
