import os
import sys
from typing import NamedTuple, Iterable, Optional

import numpy as np

from detector.events import Event, Loss
from pattern.ge_params import GEParams
from pattern.read_losses_from_csv import read_losses_from_csv, SEQUENCE_COL


class GilbertCounts(NamedTuple):
    """Approximates parameters of the Gilbert model from events by using counts of loss,
    double loss bursts, triple loss bursts and 1-0-1 loss bursts using method proposed in:

        Gilbert, E.N.: Capacity of a Burst-Noise Channel. Bell System Technical Journal 39

    TL;DR:
    assume error-free good state: k=1 (this is the Gilbert Model)
    maintain a = P(1), b = P(1|1), P(101), P(111)
    compute c = P(111) / (P(101) + P(111)), then derive params as
            1 - r = (a * c - b * b) / (2*a*c - b * (a + c))
            h = 1 - (b / (1 - r))
            p = a * r / (1 - h - a)
    """
    packet: int = 0
    loss: int = 0
    burst_11: int = 0
    burst_101: int = 0
    burst_111: int = 0

    @classmethod
    def from_events(cls, period: int, events: Iterable[Event]) -> 'GilbertCounts':
        loss_offsets = (event.offset for event in events if isinstance(event, Loss))
        return GilbertCounts.from_loss_offsets(period, loss_offsets)

    @classmethod
    def from_loss_offsets(cls, period: int, offsets: Iterable[int]) -> 'GilbertCounts':
        offsets = np.fromiter(offsets, dtype=int)
        if len(offsets) == 1:
            return GilbertCounts(packet=1, loss=1)
        diff = np.diff(offsets)
        return GilbertCounts(packet=GilbertCounts._count_packets(period, offsets),
                             loss=len(offsets),
                             burst_11=int(np.sum(diff == 1)),
                             burst_101=int(np.sum(diff == 2)),
                             burst_111=int(np.sum(np.diff(np.where(diff == 1)[0]) == 1)))

    @staticmethod
    def _count_packets(period: int, offsets: np.array) -> int:
        if len(offsets) == 1:
            return 1
        else:
            return sum((b - a) % period for a, b in zip(offsets[:-1], offsets[1:]))

    def to_params(self, simplify_h: bool = False) -> Optional[GEParams]:
        """Compute Gilbert model parameters from counts. Uses h = 0.5 if `simplify_h`"""
        try:
            a, p_101, p_111 = [count / self.packet for count in (self.loss, self.burst_101,
                                                                 self.burst_111)]
            b = self.burst_11 / self.loss
            c = p_111 / (p_101 + p_111)
            one_minus_r = (a * c - b * b) / (2 * a * c - b * (a + c))
            h = 0.5 if simplify_h else 1 - b / one_minus_r
            r = 1 - one_minus_r
            p = a * r / (1 - h - a)
            return GEParams(p, r, h, k=1)
        except ZeroDivisionError:
            return None


if __name__ == '__main__':
    try:
        csv_path = sys.argv[1]
        max_length = int(sys.argv[2])
    except IndexError:
        print('Usage: $0 <csv_path>')
        sys.exit(0)

    out_dir, csv_name = os.path.split(csv_path)
    expected = None
    try:
        expected = GEParams.from_file(os.path.join(out_dir, 'netem_params.log'))
    except:
        print('Could not parse expected ge params.')

    losses = read_losses_from_csv(csv_path, SEQUENCE_COL, max_length=max_length)
    loss_offsets = [offset for offset, loss in enumerate(losses) if loss == 1]
    actual = GilbertCounts.from_loss_offsets(2**16, loss_offsets).to_params()

    if expected is not None:
        print(f'Expected: {expected.netem_format()}')
    if actual is not None:
        print(f'Actual:   {actual.netem_format()}')
    else:
        print('Could not derive params.')
