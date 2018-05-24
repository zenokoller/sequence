import os
import shlex
import subprocess
import time
from argparse import ArgumentParser
from datetime import datetime, timedelta
from typing import Callable, List

import yaml
from tqdm import tqdm

from utils.iteration import n_cycles
from utils.nanotime import nanosecond_timestamp

DATE_FMT = '%y%m%d-%H%M%S'
DEFAULT_ARGS = {
    'client': '5634 3996',
    'server': '3996'
}
START_NODE_CMD = 'docker exec -t {nodename} timeout -sINT {running_time}s python ' \
                 '/root/python/nodes/{nodename}/main.py'
DEFAULT_RUNNING_TIME = 5  # seconds
COOLDOWN_TIME = 3  # seconds


def start_node_command(nodename: str, settings: dict, running_time: int) -> List[str]:
    def option(key: str, value: str):
        return f'--{key}' if isinstance(value, bool) and value else f'--{key} {value}'

    return [
        *shlex.split(START_NODE_CMD.format(nodename=nodename, running_time=running_time)),
        *shlex.split(DEFAULT_ARGS.get(nodename, '')),
        *shlex.split(' '.join(option(key, value) for key, value in settings[nodename].items()))
    ]


class ClientServerTestbed:
    nodenames = ['client', 'server']

    def __init__(self,
                 config: dict,
                 out_base_path: str,
                 testbed_path: str,
                 post_run_fn: Callable[[int, int, str, dict], None] = None,
                 post_experiment_fn: Callable[[str, dict], None] = None):
        self.config = config
        self.node_pids = []
        self.node_logs = {}
        self.out_path = os.path.join(out_base_path, f'{self.config["name"]}',
                                     f'{datetime.now().strftime(DATE_FMT)}')
        self.csv_path = os.path.join(self.out_path, 'results.csv')
        self.testbed_path = testbed_path
        self.post_run_fn = post_run_fn
        self.post_experiment_fn = post_experiment_fn

    def start(self):
        os.chdir(self.testbed_path)

        print(f'>>> Starting Testbed. Outputs at {self.out_path}\n')
        self.check_containers()
        self.create_out_dir()
        self.create_node_logs()

        repeats = self.config.get('repeats', 1)
        running_time = self.config.get('running_time', DEFAULT_RUNNING_TIME)
        node_settings = self.get_node_settings()
        total_runs = repeats * len(node_settings)
        print(f'>>> Running {repeats} repeats of {len(node_settings)} settings for {running_time}s,'
              f' expected running time: ~{timedelta(seconds=total_runs * running_time)}\n')

        for settings in tqdm(n_cycles(node_settings, repeats), total=total_runs):
            self.run(settings, running_time)

        self.post_experiment()
        self.close_node_logs()

    def check_containers(self):
        print('>>> Making sure containers are running...\n')
        for nodename in self.nodenames:
            cmd = ['docker-compose', 'ps', '-q', nodename]
            result = subprocess.run(cmd, stdout=subprocess.PIPE)
            if len(result.stdout) == 0:
                print(f'>>> Node `{nodename}` must be running, run `make up` or `make build-up`.')
                exit()

    def create_out_dir(self):
        os.makedirs(self.out_path, exist_ok=True)

    def create_node_logs(self):
        for nodename in self.nodenames:
            paths = (os.path.join(self.out_path, f'{nodename}_{output}.log')
                     for output in ('stdout', 'stderr'))
            log_files = tuple(open(path, 'w') for path in paths)
            self.node_logs[nodename] = log_files

    def run(self, node_settings: dict, running_time: int):
        start_time = nanosecond_timestamp()
        self.start_nodes(node_settings, running_time)
        time.sleep(running_time + COOLDOWN_TIME)
        end_time = nanosecond_timestamp()
        self.post_run(start_time, end_time, node_settings)

    def start_nodes(self, settings: dict, running_time: int):
        for nodename in self.nodenames:
            args = start_node_command(nodename, settings, running_time)
            stdout, stderr = self.node_logs[nodename]
            process = subprocess.Popen(args, stdout=stdout, stderr=stderr)
            self.node_pids.append(process.pid)

    def post_run(self, start_time: int, end_time: int, node_settings: dict):
        if self.post_run_fn is not None:
            self.post_run_fn(start_time, end_time, self.csv_path, node_settings)

    def post_experiment(self):
        if self.post_experiment_fn is not None:
            self.post_experiment_fn(self.csv_path, self.config.get('name', None))

    def get_node_settings(self) -> List[dict]:
        def apply_all(settings: dict) -> dict:
            common_settings = settings.copy().pop('all') if 'all' in settings else {}
            return {nodename: {**settings.get(nodename, {}), **common_settings}
                    for nodename in self.nodenames}

        base_settings = apply_all(self.config['settings'])
        overrides = self.config.get('override_settings', None)
        return [base_settings] if overrides is None else [
            {nodename: {**base_settings[nodename], **apply_all(override)[nodename]}
             for nodename in self.nodenames} for override in overrides]

    def close_node_logs(self):
        for stdout, stderr in self.node_logs.values():
            stdout.close()
            stderr.close()


def main(testbed_cls, config_file: str = None):
    parser = ArgumentParser()
    parser.add_argument('-c', '--config_path', type=str)
    parser.add_argument('-o', '--out_dir', type=str)
    parser.add_argument('-t', '--testbed_path', type=str)
    args = parser.parse_args()

    config_path = os.path.join(os.path.dirname(__file__), config_file or args.config_path)
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file)

    experiment = testbed_cls(config, args.out_dir, args.testbed_path)
    experiment.start()


if __name__ == '__main__':
    main(ClientServerTestbed)
