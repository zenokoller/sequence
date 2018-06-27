#!/usr/bin/env python
import os
import sys
from collections import Iterable

import matplotlib

matplotlib.use('pdf')
from matplotlib import pyplot as plt

import numpy as np
import pandas as pd

plt.style.use('seaborn')

DF_NAMES = ['hmm', 'gilbert']
LINESTYLES = ['-', ':']
PARAM_NAMES = ['p', 'r', 'h']
COLORS = ['#4C72B0', '#55A868', '#C44E52', '#8172B2']
NROWS = 3  # One row per configuration


def plot(hdf5_path: str):
    with pd.HDFStore(hdf5_path) as store:
        dfs = {name: store[name] for name in DF_NAMES}

    fig, axes = plt.subplots(nrows=NROWS, ncols=3, figsize=(10, 3 * NROWS))

    for name, linestyle in zip(DF_NAMES, LINESTYLES):
        plot_df(dfs[name], axes, linestyle, name)

    fig.tight_layout()
    plt.legend()

    out_dir, hdf5_name = os.path.split(hdf5_path)
    name, _ = hdf5_name.split('.')
    plt.savefig(os.path.join(out_dir, f'{name}.pdf'))


def plot_df(df: pd.DataFrame, axes: Iterable, linestyle: str, name: str):
    """Plot of ECDF of the relative error between the expected and actual parameter for the
    Gilbert parameters p, r, h for all values of `actual_params`."""
    df['expected_params'] = df[['p_exp', 'r_exp', 'h_exp']].apply(
        lambda x: 'p: {:.3f}, r: {:.2f}, h: {:.2f}'.format(*x),
        axis=1)
    all_expected_params = df['expected_params'].unique()

    for params, row_axes in zip(all_expected_params, axes):
        plot_row(df, params, row_axes, linestyle, name)


def plot_row(df: pd.DataFrame, expected_params: str, row_axes: Iterable, linestyle: str, name: str):
    relevant_df = df[df['expected_params'] == expected_params]
    trace_lengths = relevant_df['trace_length'].unique()

    rel_err_df = pd.DataFrame([{**{'trace_length': tup.trace_length},
                                **rel_errs(tup)
                                } for tup in relevant_df.itertuples()])

    for trace_length, color in zip(trace_lengths, COLORS):
        df_ = rel_err_df[rel_err_df['trace_length'] == trace_length]
        for (i, ax), param_name in zip(enumerate(row_axes), PARAM_NAMES):
            series = df_[param_name].sort_values()
            cdf = np.linspace(0., 1., len(series))
            label = f'{name}/{trace_length}'
            pd.Series(cdf, index=series).plot(ax=ax,
                                              label=label,
                                              color=color,
                                              linestyle=linestyle,
                                              linewidth=1.0)
            if i == 1:
                ax.set_title(expected_params, fontsize=12)


def rel_errs(tup) -> dict:
    def rel_err(exp, act):
        return abs(act - exp) / (1 + exp)

    return {
        'p': rel_err(tup.p_exp, tup.p_act),
        'r': rel_err(tup.r_exp, tup.r_act),
        'h': rel_err(tup.h_exp, tup.h_act),
    }


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
        hdf5_path = sys.argv[1]
        df_name = sys.argv[2]
    except IndexError:
        print('Usage: $0 <hdf5_path>')
        sys.exit(0)

    plot(hdf5_path)
