
import os
import time
import subprocess
from src.DataJoin.settings import http_server_logger


def current_timestamp():
    return int(time.time() * 1000)


def run_subprocess(config_dir, process_cmd, log_dir=None):
    http_server_logger.info('Starting process command: {}'.format(process_cmd))
    http_server_logger.info(' '.join(process_cmd))
    os.makedirs(config_dir, exist_ok=True)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    std_log = open(os.path.join(log_dir if log_dir else config_dir, 'std.log'), 'w')
    pid_path = os.path.join(config_dir, 'pid')

    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
    else:
        startupinfo = None
    p = subprocess.Popen(process_cmd,
                         stdout=std_log,
                         stderr=std_log,
                         startupinfo=startupinfo
                         )
    with open(pid_path, 'w') as f:
        f.truncate()
        f.write(str(p.pid) + "\n")
        f.flush()
    return p
