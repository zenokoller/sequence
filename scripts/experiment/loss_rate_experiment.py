import os
from argparse import ArgumentParser
from functools import partial
from queue import Queue
from threading import Thread

from influxdb import DataFrameClient

from scripts.experiment.base_experiment import BaseExperiment, start_experiment
from scripts.experiment.experiment_utils import repeatedly_configure_netem, reset_netem

"""Run an experiment while cycling configurations."""
NETEM_CONFS = [
    'conf/loss_rate/random_0125.conf',
    'conf/loss_rate/random_025.conf',
    'conf/loss_rate/random_05.conf',
    'conf/loss_rate/random_1.conf',
    'conf/loss_rate/random_2.conf',
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

    sequence_df = client.query(
        f'select "losses", "packets" '
        f'from "telegraf"."autogen"."httpjson_knownsequence" '
        f'where time > {start_time} and time < {end_time};')['httpjson_knownsequence']

    domain = "client-domain-uplink"
    netem_df = client.query(
        f'select "{domain}.packet.dropped" AS "losses", "{domain}.packet.count" AS "packets" '
        f'from "telegraf"."autogen"."httpjson_netem" '
        f'where time > {start_time} and time < {end_time};')['httpjson_netem']

    # bucketize data
    sequence_df = sequence_df.diff()

    diff_df = netem_df.diff()
    diff_df[diff_df < 0] = netem_df[diff_df < 0]  # netemd values are regularly reset
    netem_df = diff_df

    def compute_loss_rate(df, losses_name, packets_name):
        return (df[losses_name] / (df[losses_name] + df[packets_name])).fillna(0)

    joined_df = sequence_df.join(netem_df, lsuffix="_sequence", rsuffix="_netem")

    # Use netem packet counts to calculate sequence loss rate as shortcut to getting packet counts
    # from offsets in each interval
    joined_df['rate_sequence'] = compute_loss_rate(joined_df, 'losses_sequence', 'packets_netem')
    joined_df['rate_netem'] = compute_loss_rate(joined_df, 'losses_netem', 'packets_netem')

    # Where netem failed to count packets, set the loss rate to zero
    joined_df['rate_sequence'][joined_df['packets_netem'] == 0] = 0

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
    out_dir = start_experiment(RateExperiment, config='config/rate_2_bit.yml',
                               out_dir=args.out_dir, testbed_path=args.testbed_path)
    thread.join()

    with open(os.path.join(out_dir, 'repeated_netem_confs.log'), 'w+') as confs_log:
        while not log_queue.empty():
            timestamp, conf = log_queue.get()
            confs_log.write(f'{timestamp},{conf}\n')
