#!/usr/bin/env python
import os
import sys

import matplotlib
import pandas as pd

matplotlib.use('TKAgg')
from matplotlib import pyplot as plt

import matplotlib.ticker as mtick


def plot(csv_path: str, title: str):
    df = pd.read_csv(csv_path, index_col=0)
    df.index = pd.to_datetime(df.index)
    df = df.filter(['rate_sequence', 'rate_netem'])
    ax = df.plot(grid=True)
    ax.set_title(title, fontsize=14)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

    out_dir, csv_name = os.path.split(csv_path)
    name, _ = csv_name.split('.')
    plt.savefig(os.path.join(out_dir, f'{name}.png'))


def print_mean_rates(csv_path):
    df = pd.read_csv(csv_path, index_col=0)
    mean_rate_seq, mean_rate_netem = [df[name].mean() for name in ['rate_sequence', 'rate_netem']]
    print(f'Mean rates:\n-----------\nnetem:{mean_rate_netem}\nsequence:{mean_rate_seq}')


if __name__ == '__main__':
    try:
        csv_path = sys.argv[1]
        title = sys.argv[2]
    except IndexError:
        print('Usage: $0 <csv_path> <title>')
        sys.exit(0)

    plot(csv_path, title)
    print_mean_rates(csv_path)
