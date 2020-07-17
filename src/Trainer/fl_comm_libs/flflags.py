import tensorflow as tf

tf.flags.DEFINE_string("role", "leader", "FL worker role [leader, follower].")
tf.flags.DEFINE_string("appli_id", "jdfl", "Application Id.")

tf.flags.DEFINE_string("local_addr", None,
    "FL train local worker IP port(ip:port).")
tf.flags.DEFINE_string("peer_addr", None,
    "FL train remote worker IP port(ip:port).")
tf.flags.DEFINE_string("dc_addr", None,
    "FL train DataCenter IP port(ip:port).")
tf.flags.DEFINE_string("coordinator_addr", None,
    "FL RegisterUUID IP port(ip:port).")
tf.flags.DEFINE_string("proxy_addr", None,
    "FL proxy IP port(ip:port).")
tf.flags.DEFINE_integer("worker_id", 0, "FL train worker rank id.")
tf.flags.DEFINE_integer("rpc_service_type", 1,
    "kinds of service method: 0(Unary), 1(Bidirectional streaming).")

tf.flags.DEFINE_string("model_dir", "./models/model_dir/",
    "The directory where the checkpoint will be loaded/stored.")
tf.flags.DEFINE_string("export_dir", "./models/export_savemodel/", 
    "The directory where the exported SavedModel will be stored.")

tf.flags.DEFINE_integer("local_debug", 0,
    "local debug mode, without RegisterUUID or GetPairInfo")
tf.flags.DEFINE_integer("check_exampleid", 0,
    "check exampleid for each batch, 0: not check, 1: check")
tf.flags.DEFINE_integer("eval", 0, "eval")
tf.flags.DEFINE_string("checkpoint_hdfs_path", '',
    "hdfs checkpoint path for eval")
