#!/usr/bin/env python
import os
import sys
from itertools import chain

import matplotlib
import pandas as pd

matplotlib.use('pdf')
from matplotlib import pyplot as plt, patches

import matplotlib.ticker as mtick

plt.style.use('seaborn')

IS_BURSTY = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
LOSS_RATES = ['2%', '2%', '1%', '1%', '0.5%', '0.5%', '0.25%', '0.25%','0.125%', '0.125%']
YMAX = 0.04
LABEL_PADDING = [0.5, -0.003]
ALPHA = 0.25

def plot(out_dir: str, title: str):
    data_df = pd.read_csv(os.path.join(out_dir, 'results.csv'), index_col=0)
    data_df.index = pd.to_datetime(data_df.index)
    conf_df = pd.read_csv(os.path.join(out_dir, 'repeated_netem_confs.log'), index_col=0,
                          header=None)
    conf_df.index = pd.to_datetime(conf_df.index)

    # Use relative time axis
    data_df.index = map(lambda x: x.total_seconds(), [i - data_df.index[0]
                                                      for i in data_df.index])
    conf_df.index = map(lambda x: x.total_seconds(), [i - conf_df.index[0]
                                                      for i in conf_df.index])

    # Setup stacked suplots without space in between
    fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1, figsize=(10, 6), sharex=True)
    fig.subplots_adjust(wspace=0, hspace=0)

    # Plot patches for actual pattern (one per second)
    max_seconds = max(data_df.index)
    patch_width = 1  # second?
    for i in (i for i, is_bursty in enumerate(data_df['bursty'] == 1) if is_bursty):
        rect = patches.Rectangle((i, 0), 1, 20, color='blue', alpha=ALPHA)
        ax0.add_patch(rect)

    # Plot vertical lines and detected patches for conf changes
    plt.vlines(conf_df.index, ymin=0, ymax=YMAX, color='r', linewidth=0.5)
    deltas = zip(conf_df.index, chain.from_iterable([conf_df.index[1:], [max(data_df.index)]]))
    for (d0, d1), label, is_bursty in zip(deltas, LOSS_RATES, IS_BURSTY):
        x_pad, y_pad = LABEL_PADDING
        plt.text(d0 + x_pad, YMAX + y_pad, label, fontsize=8, color='r')
        if is_bursty:
            rect = patches.Rectangle((d0, 0), (d1 - d0), YMAX, color='blue', alpha=ALPHA)
            ax1.add_patch(rect)

    # Plot loss rate
    ax = data_df['loss_rate'].plot(grid=True, linewidth=0.75, ax=ax1)
    plt.legend(loc='upper right')

    fig.suptitle(title)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

    plt.savefig(os.path.join(out_dir, f'{title}.pdf'))


if __name__ == '__main__':
    try:
        out_dir = sys.argv[1]
        title = sys.argv[2]
    except IndexError:
        print('Usage: $0 <out_dir> <title>')
        sys.exit(0)

    plot(out_dir, title)
