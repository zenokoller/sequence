import os
import subprocess
from argparse import ArgumentParser
from itertools import repeat, chain, product

from scripts.experiment.base_experiment import start_experiment
from scripts.experiment.trace_experiment import TraceExperiment

"""Alternately reconfigure netem and run experiments."""

netem_confs = [
    'conf/ge/1-20-50.conf',
    'conf/ge/1-20-75.conf',
    'conf/ge/1-20-100.conf',
    'conf/ge/1-33-50.conf',
    'conf/ge/1-33-75.conf',
    'conf/ge/1-33-100.conf',
    'conf/ge/1-50-50.conf',
    'conf/ge/1-50-75.conf',
    'conf/ge/1-50-100.conf',
    'conf/ge/1-100-100.conf',
]

experiment_cls = TraceExperiment
experiment_confs = [
    'config/trace_2_bit.yml',
    'config/trace_3_bit.yml',
    'config/trace_4_bit.yml',
    'config/trace_8_bit.yml',
]


def configure_netem(testbed_path: str, config_file: str):
    print(f'>>> Configuring netem with {config_file}...')

    os.chdir(testbed_path)
    cmd = ['bin/link-config.bash', '-t', '-c', config_file]
    _ = subprocess.run(cmd, stdout=subprocess.PIPE)
    return


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-o', '--out_dir', type=str)
    parser.add_argument('-t', '--testbed_path', type=str)
    parser.add_argument('-r', '--repeats', type=int)
    args = parser.parse_args()

    repeated_netem_confs = chain.from_iterable(repeat(netem_confs, args.repeats))
    for netem_conf, experiment_conf in product(repeated_netem_confs, experiment_confs):
        configure_netem(args.testbed_path, netem_conf)
        start_experiment(experiment_cls, config=experiment_conf, out_dir=args.out_dir,
                         testbed_path=args.testbed_path)
