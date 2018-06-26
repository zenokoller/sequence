import os
from functools import partial

import pandas as pd
import re
import sys
from typing import Optional, Callable

from tqdm import tqdm

from pattern.gilbert_counts import main as run_gilbert
from pattern.hmm import main as run_hmm

SYMBOL_BITS_RE = "'symbol_bits': (\d+)"
COLUMNS = ['trace_length', 'symbol_bits', 'actual_params', 'expected_params']
TRACE_LENGHTS = [1000, 5000, 10000, 20000]
STORE_EACH = 10


def main(data_dir: str, out_path: str):
    for run_fn, name in zip([run_gilbert, run_hmm],
                            ['gilbert', 'hmm']):
        print(f'>>> Computing params for {name}')

        def store_df(df):
            with pd.HDFStore(out_path) as store:
                store[name] = df

        df = compute_ge_params(run_fn, data_dir, store_df, STORE_EACH)
        store_df(df)
        print(f'>>> Done!')


def compute_ge_params(run_fn: Callable, directory: str, store_fn: Callable = None,
                      store_each: int = None) -> pd.DataFrame:
    results = []

    walked = list(os.walk(directory))
    for index, (subdir, _, _) in tqdm(enumerate(walked)):
        symbol_bits = parse_symbol_bits_from_file(os.path.join(subdir, 'client.log'))
        netem_params_path = os.path.join(subdir, 'netem_params.log')
        trace_path = os.path.join(subdir, 'results.csv')

        if symbol_bits is None or not os.path.isfile(netem_params_path) or not os.path.isfile(
                trace_path):
            continue

        for trace_length in TRACE_LENGHTS:
            actual, expected = run_fn(trace_path, trace_length)

            results.append(
                {'trace_length': trace_length,
                 'symbol_bits': symbol_bits,
                 'actual_params': actual.to_percent_str(),
                 'expected_params': expected.to_percent_str()
                 })

        if store_each is not None and index % store_each == 0:
            store_fn(pd.DataFrame(results, columns=COLUMNS))

    return pd.DataFrame(results, columns=COLUMNS)


compute_with_hmm = partial(compute_ge_params, run_hmm)
compute_with_gilbert = partial(compute_ge_params, run_gilbert)


def parse_symbol_bits_from_str(string: str) -> Optional[int]:
    pattern = re.compile(SYMBOL_BITS_RE, re.MULTILINE)
    match = pattern.search(string)
    if match is not None:
        return int(match.groups()[0])
    else:
        return None


def parse_symbol_bits_from_file(logfile_path: str) -> Optional[int]:
    try:
        with open(logfile_path) as logfile:
            return parse_symbol_bits_from_str(logfile.read())
    except:
        return None


if __name__ == '__main__':
    try:
        data_dir = sys.argv[1]
        out_path = sys.argv[2]
    except KeyError:
        print('Usage: $0 <data_dir> <out_path>')
        sys.exit(0)

    main(data_dir, out_path)
