from argparse import ArgumentParser
from itertools import repeat, chain, product

from scripts.experiment.base_experiment import start_experiment
from scripts.experiment.experiment_utils import configure_netem
from scripts.experiment.trace_experiment import TraceExperiment

"""Alternately reconfigure netem and run experiments."""

NETEM_CONFS = [
    'conf/ge_estimation/25.conf',
    'conf/ge_estimation/50.conf',
    'conf/ge_estimation/75.conf',
    'conf/ge_estimation/100.conf'
]

experiment_cls = TraceExperiment
experiment_confs = [
    'config/trace_2_bit.yml'
]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-o', '--out_dir', type=str)
    parser.add_argument('-t', '--testbed_path', type=str)
    parser.add_argument('-r', '--repeats', type=int)
    args = parser.parse_args()

    repeated_netem_confs = chain.from_iterable(repeat(NETEM_CONFS, args.repeats))
    for netem_conf, experiment_conf in product(repeated_netem_confs, experiment_confs):
        configure_netem(args.testbed_path, netem_conf)
        start_experiment(experiment_cls, config=experiment_conf, out_dir=args.out_dir,
                         testbed_path=args.testbed_path)
