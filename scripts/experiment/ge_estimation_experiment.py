from argparse import ArgumentParser
from functools import partial
from itertools import repeat, chain

import pandas as pd
from influxdb import InfluxDBClient

from scripts.experiment.base_experiment import start_experiment, BaseExperiment
from scripts.experiment.influx_utils import get_actual_losses, get_detected_losses
from scripts.experiment.netem_utils import configure_netem, reset_netem

"""Alternately reconfigure netem and run experiments."""

NETEM_CONFS = [
    'conf/ge_estimation/loss_prob_50.conf',
    'conf/ge_estimation/loss_prob_75.conf',
    'conf/ge_estimation/loss_prob_100.conf'
]


def event_trace_to_csv(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Collects the loss events from InfluxDB and stores them as csv."""
    client = InfluxDBClient(database='telegraf')
    actual_losses = get_actual_losses(client, start_time, end_time)
    detected_losses = get_detected_losses(client, start_time, end_time)

    lower, upper = min(actual_losses), max(actual_losses) + 1

    loss_df = pd.DataFrame({
        'actual': [1 if i in actual_losses else 0 for i in range(lower, upper)],
        'detected': [1 if i in detected_losses else 0 for i in range(lower, upper)]})

    loss_df.to_csv(csv_path, mode='a+')


GEEstimationExperiment = partial(BaseExperiment,
                                 post_run_fn=event_trace_to_csv)
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-o', '--out_dir', type=str)
    parser.add_argument('-t', '--testbed_path', type=str)
    parser.add_argument('-r', '--repeats', type=int)
    args = parser.parse_args()

    reset_netem(args.testbed_path)

    repeated_netem_confs = chain.from_iterable(repeat(NETEM_CONFS, args.repeats))
    for netem_conf in repeated_netem_confs:
        configure_netem(args.testbed_path, netem_conf, blocking=True)
        start_experiment(GEEstimationExperiment, config='config/ge_estimation.yml',
                         out_dir=args.out_dir,
                         testbed_path=args.testbed_path)
