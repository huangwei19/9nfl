# coding=utf-8
import os,sys
import argparse
import ConfigParser
import shutil
from jinja2 import FileSystemLoader, Environment
BASEDIR=os.path.dirname(os.path.abspath(__file__))

def real_yaml_create(keywords):
    template_dir = os.path.abspath(BASEDIR + os.path.sep + 'template')
    j_env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
    datacenter_yaml = j_env.get_template('datacenter/datacenter.j2').render(**keywords)
    datacenter_svc_yaml = j_env.get_template('datacenter/datacenter_svc.j2').render(**keywords)
    if int(keywords.get('worker_num')) > 1:
        train_yaml = j_env.get_template('train_distribute/trainer.j2').render(**keywords)
    else:
        train_yaml = j_env.get_template('train_standalone/trainer.j2').render(**keywords)
    return datacenter_yaml,datacenter_svc_yaml,train_yaml

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("role", help="is leader or follower")
    parser.add_argument("task_id", help="unique index for fl task")
    parser.add_argument("app_id", help="tag for fl task")
    parser.add_argument("worker_num", default='2',help="worker number, only support distribute mode",type=int)
    parser.add_argument("train_data_start", help="train data start time")
    parser.add_argument("train_data_end", help="train data end time")
    parser.add_argument("data_source_name", help="tag for data source")
    parser.add_argument("data_num_epoch", help="epoch number for train data",type=int)
    return parser.parse_args()

def get_config():
    cf = ConfigParser.ConfigParser()
    cf.read(BASEDIR + os.path.sep + "../../conf/ResourceManager/k8s.conf")
    return cf

def create_context(args,config):
    ctx = {}
    ctx['task_id'] = args.task_id
    ctx['app_id'] = args.app_id
    ctx['train_data_start'] = args.train_data_start
    ctx['train_data_end'] = args.train_data_end
    ctx['data_source_name'] = args.data_source_name
    ctx['data_num_epoch'] = args.data_num_epoch
    ctx['worker_num'] = args.worker_num
    ctx['datacenter_ip'] = 'svc-dc-' + args.task_id
    ctx['coordinator_ip'] = config.get('coordinator','IP')
    ctx['coordinator_port'] = config.get('coordinator','Port')
    ctx['proxy_ip'] = config.get('proxy','IP')
    ctx['proxy_port'] = config.get('proxy','Port')
    if args.role == '1':
        ctx['trainer_image'] = config.get('image','leader_trainer_image')
        ctx['dc_image'] = config.get('image','leader_datacenter_image')
        ctx['data_dir'] = config.get('share_volume','leader_data_dir') 
        ctx['models_dir'] = config.get('share_volume','leader_models_dir') 
        ctx['namespace'] = 'fl-leader'
    else:
        ctx['trainer_image'] = config.get('image','follower_trainer_image')
        ctx['dc_image'] = config.get('image','follower_datacenter_image')
        ctx['data_dir'] = config.get('share_volume','leader_data_dir') 
        ctx['models_dir'] = config.get('share_volume','follower_models_dir') 
        ctx['namespace'] = 'fl-follower'
    ctx['train_cmd'] = config.get('train','entrance_file') 
    return ctx

if __name__ == '__main__':
    args = get_args()
    config = get_config()
    if args.role not in ['0','1']:
        print 'role should be 1:leader or 0:follower'
        sys.exit(-1)
    if args.worker_num < 1:
        print('You need at least one worker!')
        sys.exit(-1)
    ctx = create_context(args,config)
        
    dc_yaml_str,dc_svc_yaml_str,train_yaml_str = real_yaml_create(ctx)
    tmp_dir = BASEDIR + os.path.sep + '.jdfl_yaml_tmp_dir'
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir) 
    os.mkdir(tmp_dir)
    with open(tmp_dir + os.path.sep + 'dc.yaml','w') as fp:
        fp.write(dc_yaml_str)
    with open(tmp_dir + os.path.sep + 'dc_svc.yaml','w') as fp:
        fp.write(dc_svc_yaml_str)
    with open(tmp_dir + os.path.sep + 'train.yaml','w') as fp:
        fp.write(train_yaml_str)
    retval = os.system('kubectl apply -f %s' % tmp_dir)
    if retval != 0:
        print 'create tfjob error,exit code:' + str(retval)
        sys.exit(-3)
    shutil.rmtree(tmp_dir) 
