import os
from argparse import ArgumentParser
from functools import partial
from typing import Iterable

from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from scripts.experiment.base_experiment import BaseExperiment, start_experiment
from scripts.experiment.experiment_utils import reset_netem, configure_netem
from scripts.plot.precision_recall import plot

TITLES = ['Gilbert-Elliott 1%', 'Random 1%']
NETEM_CONFS = [
    'conf/precision_recall/ge_1.conf',
    'conf/precision_recall/random_1.conf',
]


def precision_recall_to_csv(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Collects actual and predicted losses from InfluxDB, computes precision and recall and
    stores it as csv."""
    client = InfluxDBClient(database='telegraf')
    query = f'select "offset" from "telegraf"."autogen"."{{series}}" ' \
            f'where time > {start_time} and time < {end_time};'

    def result_to_values(result: ResultSet, series: str, field: str) -> Iterable:
        return (item[field] for item in result.get_points(series))

    received = set(
        result_to_values(client.query(query.format(series='receive')), 'receive', 'offset'))
    detected_losses = set(
        result_to_values(client.query(query.format(series='loss')), 'loss', 'offset'))

    # derive actual loss offsets from received offsets
    lower, upper = min(received), max(received) + 1
    actual_losses = set([i for i in range(lower, upper) if not i in received])

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
                                   config='config/precision_recall.yml',
                                   out_dir=args.out_dir,
                                   testbed_path=args.testbed_path)

        plot(os.path.join(out_dir, 'results.csv'), title)
