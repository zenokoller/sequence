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

    # name, _ = csv_name.split('.')
    # plt.savefig(os.path.join(out_dir, f'{name}.png'))


if __name__ == '__main__':
    try:
        csv_path = sys.argv[1]
        title = sys.argv[2]
    except IndexError:
        print('Usage: $0 <csv_path> <title>')
        sys.exit(0)

    plot(csv_path, title)
