#!/usr/bin/env python
import os
import re
import sys
from typing import List, Dict

import matplotlib

from scripts.client_server_experiment import NETEM_FILENAME

matplotlib.use('TKAgg')
from matplotlib import pyplot as plt

import pandas as pd

NAMES = ('p', 'r', 'h')
TITLE_FMT = '{}; p={:.2f}, r={:.2f}, h={:.2f}'


def plot(csv_path: str, title: str):
    out_dir, csv_name = os.path.split(csv_path)
    df = pd.read_csv(csv_path, index_col=5)
    netem_params = read_netem_params(out_dir)

    fig, axes = plt.subplots(nrows=1, ncols=3, sharex=True, figsize=(10, 3))

    symbol_bits = (2, 3, 4, 8)
    sources_colors = {
        'sequence': ('#fdbe85', '#fd8d3c', '#e6550d', '#a63603'),
        'ground_truth': ('#cbc9e2', '#9e9ac8', '#756bb1', '#54278f')
    }
    for col, name in enumerate(NAMES):
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
        expected_value = netem_params.get(name, None)
        if expected_value is not None:
            ax.axhline(y=expected_value, color='r', linestyle='--', lw=2)
        remove_spines(ax)

    # Legend
    plt.subplots_adjust(left=0.05, right=0.8, top=0.8)
    plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0)

    # Column headers
    for ax, name in zip(axes, NAMES):
        ax.set_title(name)

    # Title
    title = TITLE_FMT.format(title, *(netem_params.get(name, '') for name in NAMES))
    fig.suptitle(title, fontsize=12)

    name, _ = csv_name.split('.')
    plt.savefig(os.path.join(out_dir, f'{name}.png'))


def remove_spines(ax):
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def read_netem_params(directory: str) -> Dict[str, float]:
    pattern = re.compile('loss gemodel p (\d+)% r (\d+)% 1-h (\d+)%', re.MULTILINE)
    with open(os.path.join(directory, NETEM_FILENAME)) as netem_file:
        netem_str = netem_file.read()
    match = pattern.search(netem_str)

    def adjust(value, name) -> float:
        value = float(value) / 100
        return 1.0 - value if name == 'h' else value

    if match is not None:
        return {name: adjust(value, name) for name, value in zip(NAMES, match.groups())}
    else:
        return {}


if __name__ == '__main__':
    try:
        csv_path = sys.argv[1]
        title = sys.argv[2]
    except IndexError:
        print('Usage: $0 <csv_path> <title>')
        sys.exit(0)

    plot(csv_path, title)
