#!/usr/bin/env python
import os
import sys

import matplotlib

matplotlib.use('pdf')
from matplotlib import pyplot as plt

import pandas as pd

plt.style.use('seaborn')


def plot(csv_path: str, title: str):
    df = pd.read_csv(csv_path, names=['symbol_bits', 'precision', 'recall'], index_col=0)
    agg_df = df.groupby('symbol_bits').mean()

    fig, ax = plt.subplots()
    agg_df.plot('precision', 'recall', marker='o', legend=None, ax=ax)

    for k, v in agg_df.iterrows():
        ax.annotate(k, v,
                    xytext=(10, -5), textcoords='offset points',
                    family='sans-serif', fontsize=20, color='darkslategrey')

    plt.title(title, fontsize=20)
    plt.xlabel('Precision', fontsize=20)
    plt.ylabel('Recall', fontsize=20)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    out_dir, csv_name = os.path.split(csv_path)
    name, _ = csv_name.split('.')
    plt.savefig(os.path.join(out_dir, f'{name}.pdf'))


if __name__ == '__main__':
    try:
        csv_path = sys.argv[1]
        title = sys.argv[2]
    except IndexError:
        print('Usage: $0 <csv_path> <title>')
        sys.exit(0)

    plot(csv_path, title)
