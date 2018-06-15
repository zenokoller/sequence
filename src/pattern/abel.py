import sys

import numpy as np
import os
from itertools import tee, groupby
from typing import NamedTuple, Iterable, List, Optional

from pattern.ge_params import GEParams
from pattern.read_losses_from_csv import RECEIVED_COL, read_losses_from_csv, SEQUENCE_COL
from utils.iteration import len_iter


class ABEL(NamedTuple):
    """Approximates parameters of the Gilbert model from events by using average burst error length.
    """
    packets: int = 0
    burst_lenghts: List[int] = 0

    @classmethod
    def from_losses(cls, losses: Iterable[int]) -> 'ABEL':
        events_a, events_b = tee(losses)
        return ABEL(packets=len_iter(events_a),
                    burst_lenghts=[len_iter(run) for val, run in groupby(events_b) if val])

    def to_params(self) -> Optional[GEParams]:
        """Compute Gilbert model parameters from burst lengths."""
        try:
            p = sum(self.burst_lenghts) / self.packets
            r = float(1 / np.mean(self.burst_lenghts))
            return GEParams(p, r, h=0, k=1)
        except ZeroDivisionError:
            return None


def main(csv_path: str, max_length: int, use_received: bool = False, verbose: bool = False):
    out_dir, csv_name = os.path.split(csv_path)
    expected = None
    try:
        expected = GEParams.from_file(os.path.join(out_dir, 'netem_params.log'))
    except:
        print('Could not parse expected ge params.')

    column = RECEIVED_COL if use_received else SEQUENCE_COL
    losses = read_losses_from_csv(csv_path, column, max_length=max_length)
    actual = ABEL.from_losses(losses).to_params()

    if verbose:
        if expected is not None:
            print(f'Expected: {expected.netem_format()}')
        if actual is not None:
            print(f'Actual:   {actual.netem_format()}')
        else:
            print('Could not derive params.')

    return actual, expected


if __name__ == '__main__':
    try:
        csv_path = sys.argv[1]
        max_length = int(sys.argv[2])
    except IndexError:
        print('Usage: $0 <csv_path> <max_length>')
        sys.exit(0)

    main(csv_path, max_length, verbose=True)
