import os
from argparse import ArgumentParser
from functools import partial
from queue import Queue
from threading import Thread

from influxdb import DataFrameClient

from scripts.experiment.base_experiment import BaseExperiment, start_experiment
from scripts.experiment.data_utils import compute_rate
from scripts.experiment.influx_utils import get_sequence_df, get_netem_df
from scripts.experiment.netem_utils import reset_netem, repeatedly_configure_netem
from scripts.plot.reorder_rate_plot import plot

TITLES = ['Reordering Configurations (2 symbol_bits)', 'Reordering Configurations (8 symbol_bits)']
# TITLES = ['Reordering and Loss Configurations (2 symbol_bits)',
#           'Reordering and Loss Configurations (8 symbol_bits)']
EXPERIMENT_CONFS = ['config/reorder_rate_2.yml', 'config/reorder_rate_8.yml']
NETEM_CONFS = [
    'conf/loss_rate/random_2.conf',
    'conf/reorder_rate/reorder_0125_delay_10.conf',
    'conf/reorder_rate/reorder_025_delay_10.conf',
    'conf/reorder_rate/reorder_05_delay_10.conf',
    'conf/reorder_rate/reorder_1_delay_10.conf',
    'conf/reorder_rate/reorder_2_delay_10.conf',
    # 'conf/reorder_rate/reorder_0125_loss_0125_delay_10.conf',
    # 'conf/reorder_rate/reorder_025_loss_025_delay_10.conf',
    # 'conf/reorder_rate/reorder_05_loss_05_delay_10.conf',
    # 'conf/reorder_rate/reorder_1_loss_1_delay_10.conf',
]
INTERVAL = 15.  # seconds


def reordering_rate_to_csv(start_time: int, end_time: int, csv_path: str, _: dict):
    """Computes reordering rate as of RFC4737 for each interval and writes to file, along with
    actual reordering rate."""
    client = DataFrameClient(database='telegraf')
    sequence_df = get_sequence_df(client, start_time, end_time)
    netem_df = get_netem_df(client, start_time, end_time)
    joined_df = sequence_df.join(netem_df, lsuffix="_sequence", rsuffix="_netem")

    # Use sequence packet counts to netem sequence to prevent netem oddities
    joined_df['loss_sequence'] = compute_rate(joined_df, 'losses_sequence', 'packets')
    joined_df['loss_netem'] = compute_rate(joined_df, 'losses_netem', 'packets')
    joined_df['reordering_sequence'] = compute_rate(joined_df, 'reorders_sequence', 'packets')
    joined_df['reordering_netem'] = compute_rate(joined_df, 'reorders_netem', 'packets')

    joined_df.to_csv(csv_path)


RateExperiment = partial(BaseExperiment,
                         post_run_fn=reordering_rate_to_csv)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-o', '--out_dir', type=str)
    parser.add_argument('-t', '--testbed_path', type=str)
    args = parser.parse_args()

    for experiment_conf, title in zip(EXPERIMENT_CONFS, TITLES):
        reset_netem(args.testbed_path)

        log_queue = Queue()
        thread = Thread(target=repeatedly_configure_netem,
                        args=(args.testbed_path, NETEM_CONFS, INTERVAL, log_queue))
        thread.start()
        out_dir = start_experiment(RateExperiment,
                                   config=experiment_conf,
                                   out_dir=args.out_dir,
                                   testbed_path=args.testbed_path)
        thread.join()

        with open(os.path.join(out_dir, 'repeated_netem_confs.log'), 'w+') as confs_log:
            while not log_queue.empty():
                timestamp, conf = log_queue.get()
                confs_log.write(f'{timestamp},{conf}\n')

        plot(out_dir, title)
