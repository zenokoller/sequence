import os
from argparse import ArgumentParser
from functools import partial

from influxdb import InfluxDBClient

from scripts.experiment.base_experiment import BaseExperiment, start_experiment
from scripts.experiment.influx_utils import get_actual_losses, \
    get_detected_losses, get_actual_reorders, get_detected_reorders
from scripts.experiment.netem_utils import reset_netem, configure_netem
from scripts.plot.loss_precision_recall_plot import plot

TITLES = ['Reordering 1% (5ms)', 'Random Loss 1%/Reordering 1% (5ms)', 'Reordering 1% (10ms)',
          'Random Loss 1%/Reordering 1% (10ms)']
NETEM_CONFS = [
    'conf/reorder_precision_recall/reorder_1_delay_5.conf',
    'conf/reorder_precision_recall/reorder_1_loss_1_delay_5.conf',
    'conf/reorder_precision_recall/reorder_1_delay_10.conf',
    'conf/reorder_precision_recall/reorder_1_loss_1_delay_10.conf',
]


def precision_recall_to_csv(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Collects actual and predicted losses and reordering from InfluxDB, computes precision and
    recall and stores it as csv."""
    client = InfluxDBClient(database='telegraf')
    actual_losses = get_actual_losses(client, start_time, end_time)
    detected_losses = get_detected_losses(client, start_time, end_time)
    actual_reorders = get_actual_reorders(client, start_time, end_time)
    detected_reorders = get_detected_reorders(client, start_time, end_time)

    # compute precision and recall
    loss_true_positives = len(actual_losses.intersection(detected_losses))
    loss_positives = len(detected_losses)
    loss_relevant = len(actual_losses)
    loss_precision = loss_true_positives / loss_positives if loss_positives > 0 else 0
    loss_recall = loss_true_positives / loss_relevant if loss_relevant > 0 else 0

    common_offsets = set(actual_reorders.keys()).intersection(detected_reorders.keys())
    reorder_true_positives = sum(1 if actual_reorders[offset] == detected_reorders[offset] else 0
                                 for offset in common_offsets)
    reorder_positives = len(detected_reorders)
    reorder_relevant = len(actual_reorders)
    reorder_precision = reorder_true_positives / reorder_positives if reorder_positives > 0 else 0
    reorder_recall = reorder_true_positives / reorder_relevant if reorder_positives > 0 else 0

    symbol_bits = settings['client']['symbol_bits']
    with open(csv_path, 'a+') as out_file:
        out_file.write(
            f'{symbol_bits},{loss_precision},{loss_recall},{reorder_precision},{reorder_recall}\n')


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
                                   config='config/reorder_precision_recall.yml',
                                   out_dir=args.out_dir,
                                   testbed_path=args.testbed_path)

        plot(os.path.join(out_dir, 'results.csv'), title)
