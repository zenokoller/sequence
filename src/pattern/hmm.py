import os
import sys

import numpy as np
from hmmlearn.hmm import MultinomialHMM

from pattern.ge_params import GEParams
from pattern.read_losses_from_csv import read_losses_from_csv, SEQUENCE_COL, RECEIVED_COL

startprob_prior = np.array(
    [0.99, 0.01]
)

transmat_prior = np.array(
    [[0.95, 0.05],
     [0.95, 0.05]]
)

emissionprob_prior = np.array(
    [[0.9, 0.1],
     [0.1, 0.9]]
)

model = MultinomialHMM(n_components=2, verbose=False, n_iter=1000, tol=1e-3)
model.startprob_ = startprob_prior
model.transmat_ = transmat_prior
model.emissionprob_ = emissionprob_prior
model.init_params = 'st'


def fit_ge_params(losses: np.array) -> GEParams:
    model.fit(losses)
    return GEParams.from_hmm(model)


def main(csv_path: str, max_length: int, use_received: bool = False, verbose: bool = False):
    out_dir, csv_name = os.path.split(csv_path)
    expected = None
    try:
        expected = GEParams.from_file(os.path.join(out_dir, 'netem_params.log'))
    except:
        print('Could not parse expected ge params.')

    column = RECEIVED_COL if use_received else SEQUENCE_COL
    losses = read_losses_from_csv(csv_path, column, max_length=max_length)
    actual = fit_ge_params(losses)

    if verbose:
        print(f'Actual:   {actual.netem_format()}')
        if expected is not None:
            print(f'Expected: {expected.netem_format()}')

    return actual, expected


if __name__ == '__main__':
    try:
        csv_path = sys.argv[1]
        max_length = int(sys.argv[2])
    except IndexError:
        print('Usage: $0 <csv_path> <max_length>')
        sys.exit(0)

    main(csv_path, max_length, use_received=True, verbose=True)
