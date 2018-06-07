import os
import subprocess
from argparse import ArgumentParser

from scripts.client_server_experiment import start_experiment
from scripts.trace_only.experiment import TraceOnlyExperiment

"""Alternately reconfigure netem and run experiments."""

# TODO: Specify via args
netem_confs = [
    'conf/loss_gilbert_1.conf',
    'conf/loss_random_1.conf',
]

experiment_cls = TraceOnlyExperiment
experiment_conf = 'trace_only/config.yml'


def configure_netem(testbed_path: str, config_file: str):
    print(f'>>> Configuring netem with {config_file}...')

    os.chdir(testbed_path)
    cmd = ['bin/link-config.bash', '-t', '-c', config_file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    print(result.stdout)
    return

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-o', '--out_dir', type=str)
    parser.add_argument('-t', '--testbed_path', type=str)
    args = parser.parse_args()

    for conf in netem_confs:
        configure_netem(args.testbed_path, conf)
        start_experiment(experiment_cls, config=experiment_conf, out_dir=args.out_dir,
                         testbed_path=args.testbed_path)
