#!/usr/bin/env python
import os
import sys
from collections import Iterable
from itertools import chain

import matplotlib

from pattern.ge_params import GEParams

matplotlib.use('pdf')
from matplotlib import pyplot as plt

import numpy as np
import pandas as pd

plt.style.use('seaborn')

PARAM_NAMES = ['p', 'r', 'h']


def plot(hdf5_path: str, df_name: str):
    """Plot of ECDF of the relative error between the expected and actual parameter for the
    Gilbert parameters p, r, h for all values of `actual_params`."""
    with pd.HDFStore(hdf5_path) as store:
        df = store[df_name]

    def plot_row(expected_params_str: str, row_axes: Iterable):
        expected = GEParams.from_str(expected_params_str)
        relevant_df = df[df['expected_params'] == expected_params_str]
        trace_lengths = relevant_df['trace_length'].unique()

        rel_error_df = pd.DataFrame(
            list(chain.from_iterable([{**{'trace_length': trace_length},
                                       **expected.rel_errors(GEParams.from_str(actual_str))}
                                      for actual_str in relevant_df[relevant_df['trace_length'] ==
                                                                    trace_length][
                                          'actual_params']]
                                     for trace_length in trace_lengths)))

        for trace_length in trace_lengths:
            df_ = rel_error_df[rel_error_df['trace_length'] == trace_length]
            for ax, param_name in zip(row_axes, PARAM_NAMES):
                series = df_[param_name].sort_values()
                cdf = np.linspace(0., 1., len(series))
                pd.Series(cdf, index=series).plot(ax=ax, label=trace_length)
        ax.set_title(expected, fontsize=12)

    all_expected_params = df['expected_params'].unique()
    nrows = len(all_expected_params)

    fig, axes = plt.subplots(nrows=nrows, ncols=3, figsize=(10, 3))
    for params, row in zip(all_expected_params, axes):
        plot_row(params, row)

    plt.suptitle(title, fontsize=14)

    out_dir, hdf5_name = os.path.split(hdf5_path)
    name, _ = hdf5_name.split('.')
    plt.savefig(os.path.join(out_dir, f'{df_name}.pdf'))


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
        title = sys.argv[3]
    except IndexError:
        print('Usage: $0 <hdf5_path> <df_name> <title>')
        sys.exit(0)

    plot(hdf5_path, df_name)
