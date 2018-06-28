#!/usr/bin/env python
import os
import sys
from itertools import chain

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use('pdf')
from matplotlib import pyplot as plt

plt.style.use('seaborn')

CONDITIONS = [
    'random_05', 'random_1', 'random_2', 'ge_05', 'ge_1', 'ge_2'
]


def plot(base_path: str, title: str):
    """Plots small multiples of ecdfs for batch_size vs packet latency for different loss
    conditions.
    Note: Uses `base_path/condition/results.csv` for each condition in CONDITIONS
    """
    df = pd.concat(read_df(csv_path(base_path, condition), condition) for condition in CONDITIONS)

    fig, axes = plt.subplots(nrows=2, ncols=3, sharex=True, figsize=(10, 5))
    for ax, condition in zip(chain.from_iterable(axes), CONDITIONS):
        cond_df = df[df.condition == condition]
        for label, values in cond_df.groupby(cond_df.index):
            series = values.packet_latency.sort_values()
            cdf = np.linspace(0., 1., len(series))
            pd.Series(cdf, index=series).plot(ax=ax, label=label, linewidth=1.0)
        ax.set_title(condition, fontsize=12)
    plt.suptitle(title, fontsize=14)
    plt.legend()
    plt.savefig(os.path.join(base_path, f'packet_latency_ecdf.pdf'))


def csv_path(base_path: str, condition: str) -> str:
    return os.path.join(base_path, f'{condition}/results.csv')


def read_df(csv_path: str, condition: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path,
                     names=['batch_size', 'packet_latency'],
                     index_col=0)
    df['condition'] = condition
    return df


if __name__ == '__main__':
    try:
        base_path = sys.argv[1]
        title = sys.argv[2]
    except IndexError:
        print('Usage: $0 <base_path> <title>')
        sys.exit(0)

    plot(base_path, title)
