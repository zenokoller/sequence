#!/usr/bin/env python
import os
import sys

import matplotlib
import pandas as pd

matplotlib.use('pdf')
from matplotlib import pyplot as plt

import matplotlib.ticker as mtick

plt.style.use('seaborn')

SKIP_FIRST = 13  #seconds
LINES_LABELS = ['0.125%', '0.25%', '0.5%', '1%', '2%']
YMAX = 0.04
LABEL_PADDING = [0.5, -0.003]


def plot(out_dir: str, title: str):
    data_df = pd.read_csv(os.path.join(out_dir, 'results.csv'), index_col=0)
    data_df.index = pd.to_datetime(data_df.index)
    conf_df = pd.read_csv(os.path.join(out_dir, 'repeated_netem_confs.log'), index_col=0,
                          header=None)
    conf_df.index = pd.to_datetime(conf_df.index)

    # SKIP_FIRST seconds
    data_df = data_df.iloc[SKIP_FIRST:]
    conf_df = conf_df.iloc[1:]

    # Use relative time axis
    data_df.index = map(lambda x: x.total_seconds(), [i - data_df.index[0]
                                                      for i in data_df.index])
    conf_df.index = map(lambda x: x.total_seconds(), [i - conf_df.index[0]
                                                      for i in conf_df.index])

    # Plot data
    data_df = data_df.filter(['rate_sequence', 'rate_netem'])
    data_df.columns = ['detected', 'actual']
    ax = data_df.plot(grid=True, figsize=(9, 3), linewidth=0.75)
    plt.legend(loc='upper right')

    # Plot vertical lines for conf changes
    plt.vlines(conf_df.index, ymin=0, ymax=YMAX, color='r', linewidth=0.5)
    for delta, label in zip(conf_df.index, LINES_LABELS):
        x_pad, y_pad = LABEL_PADDING
        plt.text(delta + x_pad, YMAX + y_pad, label, fontsize=8, color='r')

    ax.set_title(title, fontsize=14)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    plt.xlabel('Time [seconds]')
    plt.ylabel('Loss rate')
    plt.gcf().subplots_adjust(bottom=0.15)

    plt.savefig(os.path.join(out_dir, f'{title}.pdf'))


if __name__ == '__main__':
    try:
        out_dir = sys.argv[1]
        title = sys.argv[2]
    except IndexError:
        print('Usage: $0 <out_dir> <title>')
        sys.exit(0)

    plot(out_dir, title)
