#-*-encoding=utf-8-*-
import os
import socket
import logging
import grpc
import time
import json
import sys
import tensorflow as tf
from tensorflow.python.platform import flags
from tensorflow.python.framework import ops

from proto import co_proxy_pb2_grpc as pxy_grpc
from fl_rpc_utils import prepare_rpc_channel
import util


LEADER = "leader"
FOLLOWER = "follower"


@util.with_name_scope("verify_example_ids")
def verify_example_ids(fl_bridge, ids, debug_mode=True):
    """
    get ids_chk_op by FLAGS.role and FLAGS.check_exampleid
    """
    FLAGS = flags.FLAGS
    if FLAGS.check_exampleid == 0:
        logging.info("don't check example id")
        return tf.assert_equal(1, 1)
    
    # check exampleid
    logging.info("check example id")
    ids_x = tf.strings.to_hash_bucket_fast(ids, num_buckets = 2**31-1)
    if FLAGS.role == LEADER:
        if debug_mode:
            print_op = tf.print("_verify_example_ids:", ids_x, summarize=256,
                    output_stream=sys.stdout)
            with ops.control_dependencies([print_op]):
                ids_chk_op = fl_bridge.fl_tensor_send(ids_x,
                    datamsg_sname='_verify_example_ids')
        else:
            ids_chk_op = fl_bridge.fl_tensor_send(ids_x,
                datamsg_sname='_verify_example_ids')
    elif FLAGS.role == FOLLOWER:
        with ops.control_dependencies([ids]):
            ids_y = fl_bridge.fl_tensor_recv(T=tf.int64, 
                datamsg_rname='_verify_example_ids')
            if debug_mode:
                print_op = tf.print("_verify_example_ids:", ids_y, summarize=256,
                    output_stream=sys.stdout)
                with ops.control_dependencies([print_op]):
                    ids_chk_op = tf.assert_equal(ids_x, ids_y)
            else:
                ids_chk_op = tf.assert_equal(ids_x, ids_y)
    else:
        raise ValueError("role should be leader or follower, received %s"
            % str(role))
    return ids_chk_op


class FLEnv(object):
    def __init__(self, FLAGS):
        self._parse_mconfig(FLAGS)
        logging.info(self.mconfig)

    def fl_run_generator(self, fl_func):
        """
        如果是本地模式(无coordinator和proxy)则不需要注册和配对
        """
        if not fl_func.__call__:
            raise TypeError("fl_run should be a function")

        def func(*args, **kwargs):
            logging.info("local debug mode: %s" % self.local_debug)
            run_config = self.mconfig

            # 注册和配对
            if self.local_debug: 
                channel_comm_uuid = 'jdfl_TrainerWorkerService_%s' % \
                    run_config["worker_id"]
            else:
                channel_comm_uuid = prepare_rpc_channel(
                   run_config['coordinator_addr'], [run_config['channel_appli_id']],
                   run_config['local_addr'])
            self.mconfig["channel_comm_uuid"] = channel_comm_uuid
            
            # 目录清理
            is_chief = kwargs['is_chief']
            run_config = kwargs['run_config']
            logging.info("is_chief: %s" % is_chief)
            logging.info("run_config: %s" % run_config)

            util.rm_dir('_tmp/')
            if is_chief:
                util.mk_dir(run_config['model_dir'])
                util.rm_dir(run_config['export_dir'])
                util.run("cp %s %s" % (sys.argv[0], 'logs'))

            # checkpoint恢复，chief 首次启动时下载checkpoint
            if run_config["checkpoint_hdfs_path"]:
                # 首次启动时SUCCESS_FILE应不存在
                SUCCESS_FILE = os.path.join(run_config["model_dir"],
                    'DOWNLOAD_SUCCESS')
                if is_chief and not os.path.exists(SUCCESS_FILE):
                    util.download_from_hdfs(run_config["checkpoint_hdfs_path"], 
                        run_config["model_dir"])
                    util.run('touch %s' % SUCCESS_FILE)
                else:
                    while not os.path.exists(SUCCESS_FILE):
                        logging.info("checkpoint not restored, sleep 30s")
                        time.sleep(30)
            # 主函数
            fl_func(*args, **kwargs)

        return func

    def _parse_mconfig(self, FLAGS):
        """
        获取运行时配置，优先从环境变量拿
        """
        self.local_debug = FLAGS.local_debug == 1

        mconfig = {}
        mconfig['role'] = FLAGS.role
        # App ID
        mconfig['appli_id'] = FLAGS.appli_id
        env_appli_id = os.environ.get('AppID')
        if env_appli_id is not None:
            mconfig['appli_id'] = env_appli_id

        # worker id 
        mconfig['worker_id'] = FLAGS.worker_id
        env_worker_id = os.environ.get('worker_id')
        if env_worker_id is not None:
            mconfig['worker_id'] = env_worker_id
        
        # 和coordinator通信: 注册和配对
        channel_appli_id = '%s_TrainerWorkerService_%s' % (
            mconfig['appli_id'], mconfig['worker_id'])
        mconfig["channel_appli_id"] = channel_appli_id

        # RPC service type
        mconfig['rpc_service_type'] = FLAGS.rpc_service_type
        env_rpc_serv_type = os.environ.get('rpc_service_type')
        if env_rpc_serv_type is not None:
            mconfig['rpc_service_type'] = env_rpc_serv_type

        # Local port config
        mconfig['local_addr'] = FLAGS.local_addr
        mconfig['bind_addr'] = FLAGS.local_addr
        if FLAGS.local_addr is not None:
            port = FLAGS.local_addr.split(':')[1]
            mconfig['bind_addr'] = '[::]:'+ str(port)

        env_port = os.environ.get('worker_port')
        if env_port is not None:
            port = env_port.split(',')[0]
            local_ip = socket.gethostbyname(socket.gethostname())
            #local_ip = 'localhost'
            mconfig['local_addr'] = str(local_ip) + ':' + str(port)
            mconfig['bind_addr'] = '[::]:' + str(port)

        # unused
        mconfig['peer_addr'] = FLAGS.peer_addr

        # coordinator
        if self.local_debug and FLAGS.coordinator_addr is None:
            FLAGS.coordinator_addr = FLAGS.peer_addr
        mconfig['coordinator_addr'] = FLAGS.coordinator_addr

        env_coo_ip = os.environ.get('coordinator_ip')
        env_coo_port= os.environ.get('coordinator_port')
        if env_coo_ip is not None and env_coo_port is not None:
            mconfig['coordinator_addr'] = str(env_coo_ip) + ':' + str(env_coo_port)

        # proxy
        if self.local_debug and FLAGS.proxy_addr is None:
            # local debug mode doesn't need proxy_addr
            FLAGS.proxy_addr = FLAGS.peer_addr
        mconfig['proxy_addr'] = FLAGS.proxy_addr

        env_proxy_ip = os.environ.get('proxy_ip')
        env_proxy_port = os.environ.get('proxy_port')
        if env_proxy_ip is not None and env_proxy_port is not None:
            mconfig['proxy_addr'] = str(env_proxy_ip) + ':' + str(env_proxy_port)

        # datacenter
        mconfig['dc_addr'] = FLAGS.dc_addr
        env_dc_ip = os.environ.get('datacenter_ip')
        env_dc_port = os.environ.get('datacenter_port')
        if env_dc_ip is not None and env_dc_port is not None:
            mconfig['dc_addr'] = str(env_dc_ip) + ':' + str(env_dc_port)

        mconfig['model_dir'] = FLAGS.model_dir
        mconfig['export_dir'] = FLAGS.export_dir
        mconfig['local_debug'] = FLAGS.local_debug
        mconfig['log_dir'] = FLAGS.local_debug or 'logs'
        
        # eval
        mconfig['eval'] = FLAGS.eval
        mconfig['checkpoint_hdfs_path'] = FLAGS.checkpoint_hdfs_path

        self.mconfig = mconfig 

    def run_cluster(self, fl_run):
        """
        parse tf config and run local / distuributed cluster
        """
        fl_run = self.fl_run_generator(fl_run)

        tf_config = os.environ.get('TF_CONFIG')
        mconfig = self.mconfig

        # Run local.
        if not tf_config:
            logging.info('Start local training')
            mconfig['worker_replicas'] = 1
            return fl_run(is_chief=True, run_config=mconfig)

        logging.info('TF_CONFIG: %s' % str(tf_config))
        tf_config_json = json.loads(tf_config)
        cluster = tf_config_json.get('cluster')
        job_name = tf_config_json.get('task', {}).get('type')
        task_index = tf_config_json.get('task', {}).get('index')

        cluster_spec = tf.train.ClusterSpec(cluster)
        worker_replicas = (len(cluster_spec.as_dict().get('worker', [])) +
            len(cluster_spec.as_dict().get('chief', [])) + 
            len(cluster_spec.as_dict().get('master', [])))
        mconfig['worker_replicas'] = worker_replicas
        ps_tasks = len(cluster_spec.as_dict().get('ps', []))

        # Run local.
        if job_name is None or task_index is None:
            logging.info('Start local training')
            return fl_run(is_chief=True, run_config=mconfig)

        if worker_replicas > 1 and ps_tasks < 1:
            raise ValueError('At least 1 ps task is needed for distributed training.')

        if worker_replicas >= 1 and ps_tasks > 0:
            if job_name == 'ps':
                logging.info('Start PS')
                #cluster_spec = tf.train.ClusterSpec(cluster)
                server = tf.train.Server(cluster_spec,
                    job_name=job_name, task_index=task_index)
                server.join()
                return
            elif job_name in ['master', 'worker', 'chief']:
                logging.info('Start %s', job_name)
                return fl_run(is_chief=(job_name != 'worker'), 
                    run_config=mconfig, cluster=cluster, 
                    job_name=job_name, task_index=task_index)
        else:
            logging.info('Start local training')
            return fl_run(is_chief=True, run_config=mconfig)

    def get_mconfig(self):
        return self.mconfig

    def set_role(self, role):
        flags.FLAGS.role = role
        self.mconfig['role'] = role

    def set_local_debug(self):
        flags.FLAGS.local_debug = 1
        self.mconfig['local_debug'] = 1
        self.local_debug = True
