import os
from argparse import ArgumentParser
from functools import partial
from queue import Queue
from threading import Thread

from influxdb import DataFrameClient

from scripts.experiment.base_experiment import BaseExperiment, start_experiment
from scripts.experiment.data_utils import compute_rate
from scripts.experiment.influx_utils import get_sequence_df, get_netem_df
from scripts.experiment.netem_utils import repeatedly_configure_netem, reset_netem
from scripts.plot.loss_rate_plot import plot

TITLE = 'Random Configurations'
# TITLE = 'Gilbert-Elliott Configurations'
NETEM_CONFS = [
    'conf/loss_rate/random_2.conf',
    'conf/loss_rate/random_0125.conf',
    'conf/loss_rate/random_025.conf',
    'conf/loss_rate/random_05.conf',
    'conf/loss_rate/random_1.conf',
    'conf/loss_rate/random_2.conf',
    # 'conf/loss_rate/random_4.conf',
    # 'conf/loss_rate/random_8.conf',
    # 'conf/loss_rate/random_16.conf',
    # 'conf/loss_rate/ge_0125.conf',
    # 'conf/loss_rate/ge_025.conf',
    # 'conf/loss_rate/ge_05.conf',
    # 'conf/loss_rate/ge_1.conf',
    # 'conf/loss_rate/ge_2.conf',
]

INTERVAL = 15.  # seconds


def loss_rate_to_csv(start_time: int, end_time: int, csv_path: str, _: dict):
    """Collects loss events and netem stats from InfluxDB, computes loss rates and stores them
    as csv."""
    client = DataFrameClient(database='telegraf')
    sequence_df = get_sequence_df(client, start_time, end_time)
    netem_df = get_netem_df(client, start_time, end_time)
    joined_df = sequence_df.join(netem_df, lsuffix="_sequence", rsuffix="_netem")

    # Use sequence packet counts to netem sequence to prevent netem oddities
    joined_df['rate_sequence'] = compute_rate(joined_df, 'losses_sequence', 'packets')
    joined_df['rate_netem'] = compute_rate(joined_df, 'losses_netem', 'packets')

    joined_df.to_csv(csv_path)


RateExperiment = partial(BaseExperiment,
                         post_run_fn=loss_rate_to_csv)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-o', '--out_dir', type=str)
    parser.add_argument('-t', '--testbed_path', type=str)
    args = parser.parse_args()

    reset_netem(args.testbed_path)

    log_queue = Queue()
    thread = Thread(target=repeatedly_configure_netem,
                    args=(args.testbed_path, NETEM_CONFS, INTERVAL, log_queue))
    thread.start()
    out_dir = start_experiment(RateExperiment,
                               config='config/loss_rate.yml',
                               out_dir=args.out_dir,
                               testbed_path=args.testbed_path)
    thread.join()

    with open(os.path.join(out_dir, 'repeated_netem_confs.log'), 'w+') as confs_log:
        while not log_queue.empty():
            timestamp, conf = log_queue.get()
            confs_log.write(f'{timestamp},{conf}\n')

    plot(out_dir, TITLE)
