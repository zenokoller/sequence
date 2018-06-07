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


def plot(csv_path: str, title: str):
    # TODO: Add line plot that visualizes loss pattern
    out_dir, csv_name = os.path.split(csv_path)
    df = pd.read_csv(csv_path, index_col=0)
    netem_params = read_netem_params(out_dir)

    # name, _ = csv_name.split('.')
    # plt.savefig(os.path.join(out_dir, f'{name}.png'))


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
