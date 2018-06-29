import datetime
import os
import subprocess
import time
from typing import List


def reset_netem(testbed_path: str):
    os.chdir(testbed_path)
    cmd = ['bin/link-reset.bash', '-t']
    _ = subprocess.check_call(cmd)


def configure_netem(testbed_path: str, config_file: str, blocking: bool = False) -> str:
    print(f'>>> Configuring netem with {config_file}...')
    os.chdir(testbed_path)
    cmd = ['bin/link-config.bash', '-t', '-n', '-c', config_file]
    timestamp = datetime.datetime.now().isoformat()
    if blocking:
        _ = subprocess.check_call(cmd, stdout=subprocess.PIPE)
    else:
        _ = subprocess.run(cmd, stdout=subprocess.PIPE)
    return timestamp


def repeatedly_configure_netem(testbed_path: str,
                               config_files: List[str],
                               interval: float,
                               log_queue):
    next_times = [time.time() + i * interval for i, _ in enumerate(config_files)]
    for next_time, conf in zip(next_times, config_files):
        time.sleep(max(0, next_time - time.time()))
        timestamp = configure_netem(testbed_path, conf)
        log_queue.put((timestamp, conf))
