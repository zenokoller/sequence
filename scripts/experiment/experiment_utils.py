import os
import subprocess
import time
from typing import List

from utils.nanotime import nanosecond_timestamp


def configure_netem(testbed_path: str, config_file: str) -> int:
    print(f'>>> Configuring netem with {config_file}...')
    os.chdir(testbed_path)
    cmd = ['bin/link-config.bash', '-t', '-c', config_file]
    timestamp = nanosecond_timestamp()
    _ = subprocess.run(cmd, stdout=subprocess.PIPE)
    return timestamp


def repeatedly_configure_netem(testbed_path: str,
                               config_files: List[str],
                               interval: float,
                               log_queue):
    next_times = [time.time() + (i + 1) * interval for i, _ in enumerate(config_files)]
    for next_time, conf in zip(next_times, config_files):
        timestamp = configure_netem(testbed_path, conf)
        log_queue.put((timestamp, conf))
        time.sleep(max(0, next_time - time.time()))
