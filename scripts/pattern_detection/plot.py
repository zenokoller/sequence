#!/usr/bin/env python
import os
import sys
from itertools import product
from typing import List

import matplotlib

matplotlib.use('TKAgg')
from matplotlib import pyplot as plt

import pandas as pd


def plot(csv_path: str, title: str, expected_values: List[float] = None):
    df = pd.read_csv(csv_path, index_col=5)

    fig, axes = plt.subplots(nrows=1, ncols=3, sharex=True, figsize=(10, 3))

    names = ('p', 'r', 'h')
    expected_values = expected_values or [None, None, None]
    symbol_bits = (2, 3, 4, 8)
    sources_colors = {
        'sequence': ('#fdbe85', '#fd8d3c', '#e6550d', '#a63603'),
        'ground_truth': ('#cbc9e2', '#9e9ac8', '#756bb1', '#54278f')
    }
    for col, (name, expected_value) in enumerate(zip(names, expected_values)):
        ax = axes[col]
        for source, colors in sources_colors.items():
            for symbol_bit, color in zip(symbol_bits, colors):
                filter = (df['source'] == source) & \
                         (df['symbol_bits'] == symbol_bit)
                df[filter][name].plot(ax=ax,
                                      label=f'{symbol_bit} bits {source}',
                                      marker='o',
                                      logx=True,
                                      color=color)
        if expected_value is not None:
            ax.axhline(y=expected_value, color='r', linestyle='--', lw=2)
        remove_spines(ax)

    # Legend and title
    plt.subplots_adjust(left=0.05, right=0.8, top=0.8)
    plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0)
    fig.suptitle(title, fontsize=12)

    # Column headers
    for ax, name in zip(axes, names):
        ax.set_title(name)

    out_dir, csv_name = os.path.split(csv_path)
    name, _ = csv_name.split('.')
    plt.savefig(os.path.join(out_dir, f'{name}.png'))


def remove_spines(ax):
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


if __name__ == '__main__':
    try:
        csv_path = sys.argv[1]
        title = sys.argv[2]
        expected_values = list(map(float, sys.argv[3].split())) if len(sys.argv) == 4 else None
    except IndexError:
        print('Usage: $0 <csv_path> <title> [<expected_values>]')
        sys.exit(0)

    plot(csv_path, title, expected_values)
