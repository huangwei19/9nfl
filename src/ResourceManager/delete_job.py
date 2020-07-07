# coding=utf-8
import os,sys
import argparse
import ConfigParser

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("role", help="is leader or follower")
    parser.add_argument("task_id", help="the task id for stop")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    if args.role not in ['0','1']:
        print 'role should be 1:leader or 0:follower'
        sys.exit(-1)
    if args.role == '1':
        ns = 'fl-leader'
    else:
        ns = 'fl-follower'
    retval_deljob = os.system('kubectl delete tfjob -l instanceId=%s -n %s' % (args.task_id,ns))
    retval_delrc = os.system('kubectl delete rc -l instanceId=%s -n %s' % (args.task_id,ns))
    retval_delsvc = os.system('kubectl delete svc -l instanceId=%s -n %s' % (args.task_id,ns))
    if retval_deljob != 0 or retval_delrc != 0 or retval_delsvc != 0:
        print 'stop fljob error,exit code:' + str(retval)
        sys.exit(-1)
