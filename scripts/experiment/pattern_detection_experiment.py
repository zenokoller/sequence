import os
from argparse import ArgumentParser
from functools import partial
from queue import Queue
from threading import Thread

from influxdb import DataFrameClient

from scripts.experiment.base_experiment import BaseExperiment, start_experiment
from scripts.experiment.netem_utils import repeatedly_configure_netem, reset_netem
from scripts.plot.pattern_detection_plot import plot

BURST_LEN = 5
LOSS_PROB = 100
TITLE = f'Pattern Detection, Burst Length: {BURST_LEN}, 1-h: {LOSS_PROB}'
NETEM_CONFS = [
    'conf/pattern_detection/random_0125.conf',
    f'conf/pattern_detection/burst_{BURST_LEN}_{LOSS_PROB}/ge_2.conf',
    'conf/pattern_detection/random_2.conf',
    f'conf/pattern_detection/burst_{BURST_LEN}_{LOSS_PROB}/ge_1.conf',
    'conf/pattern_detection/random_1.conf',
    f'conf/pattern_detection/burst_{BURST_LEN}_{LOSS_PROB}/ge_05.conf',
    'conf/pattern_detection/random_05.conf',
    f'conf/pattern_detection/burst_{BURST_LEN}_{LOSS_PROB}/ge_025.conf',
    'conf/pattern_detection/random_025.conf',
    f'conf/pattern_detection/burst_{BURST_LEN}_{LOSS_PROB}/ge_0125.conf',
    'conf/pattern_detection/random_0125.conf',
]
INTERVAL = 10.  # seconds


def influx_to_csv(start_time: int, end_time: int, csv_path: str, _: dict):
    """Collects loss events and netem stats from InfluxDB, computes loss rates and stores them
    as csv."""
    client = DataFrameClient(database='telegraf')

    sequence_df = client.query(
        f'select "packets", "bursty", "mode", "median" '
        f'from "telegraf"."autogen"."httpjson_knownsequence" '
        f'where time > {start_time} and time < {end_time};')['httpjson_knownsequence']

    domain = "client-domain-uplink"
    netem_df = client.query(
        f'select "{domain}.packet.dropped" AS "losses" '
        f'from "telegraf"."autogen"."httpjson_netem" '
        f'where time > {start_time} and time < {end_time};')['httpjson_netem']

    # bucketize data
    first_packets_value = sequence_df['packets'][0]
    sequence_df['packets'] = sequence_df['packets'].diff()
    sequence_df['packets'].iloc[0] = first_packets_value

    diff_df = netem_df.diff()
    diff_df[diff_df < 0] = netem_df[diff_df < 0]  # netemd values are regularly reset
    netem_df = diff_df

    def compute_loss_rate(df, losses_name, packets_name):
        return (df[losses_name] / (df[losses_name] + df[packets_name])).fillna(0)

    joined_df = sequence_df.join(netem_df)

    # Use sequence packet counts to netem sequence to prevent netem oddities
    joined_df['loss_rate'] = compute_loss_rate(joined_df, 'losses', 'packets')

    joined_df.to_csv(csv_path)


PatternDetectionExperiment = partial(BaseExperiment,
                                     post_run_fn=influx_to_csv)

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
    out_dir = start_experiment(PatternDetectionExperiment,
                               config='config/pattern_detection.yml',
                               out_dir=args.out_dir,
                               testbed_path=args.testbed_path)
    thread.join()

    with open(os.path.join(out_dir, 'repeated_netem_confs.log'), 'w+') as confs_log:
        while not log_queue.empty():
            timestamp, conf = log_queue.get()
            confs_log.write(f'{timestamp},{conf}\n')

    plot(out_dir, TITLE)
