import os
from argparse import ArgumentParser
from functools import partial

from influxdb import InfluxDBClient

from scripts.experiment.base_experiment import BaseExperiment, start_experiment
from scripts.experiment.influx_utils import get_actual_losses, get_detected_losses
from scripts.experiment.netem_utils import reset_netem, configure_netem
from scripts.plot.loss_precision_recall_plot import plot

TITLES = ['Gilbert-Elliott 1%', 'Random 1%']
NETEM_CONFS = [
    'conf/loss_precision_recall/ge_1.conf',
    'conf/loss_precision_recall/random_1.conf',
]


def precision_recall_to_csv(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Collects actual and predicted losses from InfluxDB, computes precision and recall and
    stores it as csv."""
    client = InfluxDBClient(database='telegraf')
    actual_losses = get_actual_losses(client, start_time, end_time)
    detected_losses = get_detected_losses(client, start_time, end_time)

    # compute precision and recall
    true_positive_count = len(actual_losses.intersection(detected_losses))
    positive_count = len(detected_losses)
    relevant_count = len(actual_losses)

    precision = true_positive_count / positive_count if positive_count > 0 else 0
    recall = true_positive_count / relevant_count if relevant_count > 0 else 0

    symbol_bits = settings['client']['symbol_bits']
    with open(csv_path, 'a+') as out_file:
        out_file.write(f'{symbol_bits},{precision},{recall}\n')


PrecisionRecallExperiment = partial(BaseExperiment,
                                    post_run_fn=precision_recall_to_csv)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-o', '--out_dir', type=str)
    parser.add_argument('-t', '--testbed_path', type=str)
    args = parser.parse_args()

    reset_netem(args.testbed_path)

    for title, netem_conf in zip(TITLES, NETEM_CONFS):
        configure_netem(args.testbed_path, netem_conf, blocking=True)

        out_dir = start_experiment(PrecisionRecallExperiment,
                                   config='config/loss_precision_recall.yml',
                                   out_dir=args.out_dir,
                                   testbed_path=args.testbed_path)

        plot(os.path.join(out_dir, 'results.csv'), title)
