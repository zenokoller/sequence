#!/usr/bin/env python

import os
import sys

import matplotlib

matplotlib.use('TKAgg')
from matplotlib import pyplot as plt

import pandas as pd


def plot(csv_path: str, title: str):
    df = pd.read_csv(csv_path,
                     names=['recovery_batch_size', 'recovery_range_length', 'packet_latency'],
                     index_col=0)
    agg_df = df.groupby(['recovery_batch_size', 'recovery_range_length']).aggregate({
        'packet_latency': ['mean', 'std']})

    fig, ax = plt.subplots()
    agg_df.packet_latency['mean'].plot(yerr=agg_df.packet_latency['std'], marker='o', ax=ax)

    plt.title(title, fontsize=14)

    out_dir, csv_name = os.path.split(csv_path)
    name, _ = csv_name.split('.')
    plt.savefig(os.path.join(out_dir, f'{name}.png'))


if __name__ == '__main__':
    try:
        csv_path = sys.argv[1]
        title = sys.argv[2]
    except IndexError:
        print('Usage: $0 <csv_path> <title>')
        sys.exit(0)

    plot(csv_path, title)
