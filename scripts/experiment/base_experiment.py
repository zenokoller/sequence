import os
import shlex
import subprocess
import time
from argparse import ArgumentParser
from datetime import datetime, timedelta
from typing import Callable, List, TextIO

import yaml

from utils.iteration import n_cycles
from utils.nanotime import nanosecond_timestamp

DATE_FMT = '%y%m%d-%H%M%S'
NETEM_FILENAME = 'netem_params.log'
DEFAULT_ARGS = {
    'client': '5634 3996',
    'server': '3996'
}
START_NODE_CMD = 'docker exec -t {nodename} timeout -sINT {running_time}s python ' \
                 '/root/python/nodes/{nodename}/main.py'
DEFAULT_RUNNING_TIME = 60  # seconds
WARMUP_TIME = 3  # seconds
COOLDOWN_TIME = 3  # seconds


def start_node_command(nodename: str, settings: dict, running_time: int) -> List[str]:
    def option(key: str, value: str):
        return f'--{key}' if isinstance(value, bool) and value else f'--{key} {value}'

    return [
        *shlex.split(START_NODE_CMD.format(nodename=nodename, running_time=running_time)),
        *shlex.split(DEFAULT_ARGS.get(nodename, '')),
        *shlex.split(' '.join(option(key, value) for key, value in settings[nodename].items()))
    ]


class BaseExperiment:
    nodenames = ['server', 'client']

    def __init__(self, config: dict, out_base_path: str, testbed_path: str,
                 post_run_fn: Callable[[int, int, str, dict], None] = None):
        self.config = config
        self.node_pids = []
        self.node_stdouts = {}
        self.out_path = os.path.join(out_base_path, f'{self.config["name"]}',
                                     f'{datetime.now().strftime(DATE_FMT)}')
        self.csv_path = os.path.join(self.out_path, 'results.csv')
        self.testbed_path = testbed_path
        self.post_run_fn = post_run_fn

    def start(self) -> str:
        os.chdir(self.testbed_path)

        print(f'>>> Starting Testbed. Outputs at {self.out_path}\n')
        self.check_containers()
        self.create_out_dir()
        self.store_netem_params()
        self.create_node_logs()

        repeats = self.config.get('repeats', 1)
        running_time = self.config.get('running_time', DEFAULT_RUNNING_TIME)
        node_settings = self.get_node_settings()
        total_runs = repeats * len(node_settings)
        print(f'>>> Running {repeats} repeats of {len(node_settings)} settings for {running_time}s,'
              f' expected running time: ~{timedelta(seconds=total_runs * running_time)}\n')

        for settings in n_cycles(node_settings, repeats):
            self.run(settings, running_time)

        self.close_node_logs()
        return self.out_path

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

    def store_netem_params(self):
        print('>>> Storing netem params...\n')

        def netem_params(nodename: str):
            cmd = ['docker', 'exec', '-t', nodename, 'tc', 'qdisc', 'show']
            result = subprocess.run(cmd, stdout=subprocess.PIPE)
            return f'{nodename}:\n{str(result.stdout)}\n'

        with open(os.path.join(self.out_path, NETEM_FILENAME), 'w+') as netem_file:
            netem_file.write('\n'.join(netem_params(nodename) for nodename in self.nodenames))

    def create_node_logs(self):
        def log_file(nodename: str) -> TextIO:
            path = os.path.join(self.out_path, f'{nodename}.log')
            return open(path, 'w')

        self.node_stdouts = {nodename: log_file(nodename) for nodename in self.nodenames}

    def run(self, node_settings: dict, running_time: int):
        start_time = nanosecond_timestamp()
        self.start_nodes(node_settings, running_time)
        time.sleep(running_time + COOLDOWN_TIME)
        end_time = nanosecond_timestamp()
        self.post_run(start_time, end_time, node_settings)

    def start_nodes(self, settings: dict, running_time: int):
        for nodename in self.nodenames:
            args = start_node_command(nodename, settings, running_time)
            stdout = self.node_stdouts[nodename]
            process = subprocess.Popen(args, stdout=stdout)
            self.node_pids.append(process.pid)

    def post_run(self, start_time: int, end_time: int, node_settings: dict):
        start_time = round(start_time + WARMUP_TIME * 1e09)
        if self.post_run_fn is not None:
            self.post_run_fn(start_time, end_time, self.csv_path, node_settings)

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
        for stdout in self.node_stdouts.values():
            stdout.close()


def main(experiment_cls, config_file: str = None) -> str:
    parser = ArgumentParser()
    parser.add_argument('-c', '--config_path', type=str)
    parser.add_argument('-o', '--out_dir', type=str)
    parser.add_argument('-t', '--testbed_path', type=str)
    args = parser.parse_args()

    return start_experiment(experiment_cls,
                            config=config_file or args.config_path,
                            out_dir=args.out_dir,
                            testbed_path=args.testbed_path)


def start_experiment(experiment_cls, config: str = None, out_dir: str = None, testbed_path:
str = None) -> str:
    config_path = os.path.join(os.path.dirname(__file__), config)
    with open(config_path, 'r') as file_:
        config = yaml.load(file_)
    experiment = experiment_cls(config, out_dir, testbed_path)
    return experiment.start()


if __name__ == '__main__':
    main(BaseExperiment)
