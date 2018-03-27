from functools import partial
from typing import List, Dict

from termcolor import colored

from simulator.ground_truth.ground_truth import GroundTruth
from synchronizer.max_flow.alignment import Alignment
from synchronizer.max_flow.find_events import find_events

left_col_width = 10


def print_events(sig: List[int],
                 ref: List[int],
                 alignment: Alignment,
                 ground_truth: GroundTruth = None):
    offset, _ = alignment
    losses, reorders, dupes = find_events(alignment)
    exp_losses, exp_reorders, exp_dupes = ground_truth if ground_truth is not None \
        else (None, None, None)

    _print_dupes(sig, offset, dupes, exp_dupes)
    _print_signals(sig, ref, offset)
    _print_losses(ref, losses, exp_losses)
    _print_reorders(ref, reorders, exp_reorders)


def _print_dupes(sig: List[int], offset: int, dupes: List[int], expected_dupes: List[int] = None):
    if expected_dupes is None:
        dupes_str = ' '.join('d' if i in dupes else ' ' for i in range(len(sig)))
    else:
        print_char = partial(_print_actual_expected_char, char='d', actual=dupes,
                             expected=expected_dupes)
        dupes_str = ' '.join(print_char(i) for i in range(len(sig)))
    print(f'{"dupes".rjust(left_col_width)} | {" " * 2 * offset}{dupes_str}')


def _print_actual_expected_char(i: int,
                                char: str = None,
                                actual: list = None,
                                expected: list = None) -> str:
    if i in actual and i in expected:
        return colored(char, 'green')
    elif i in actual:
        return colored(char, 'red')
    elif i in expected:
        return colored(char, 'blue')
    else:
        return ' '


def _print_signals(sig: List[int], ref: List[int], offset: int):
    sig_str = ' ' * 2 * offset + ' '.join(str(s) for s in sig)
    print(f'{"SIGNAL".rjust(left_col_width)} | {sig_str}')
    ref_str = ' '.join(str(r) for r in ref)
    print(f'{"REFERENCE".rjust(left_col_width)} | {ref_str}')


def _print_losses(ref: List[int], losses: List[int], expected_losses: List[int] = None):
    if expected_losses is None:
        loss_str = ' '.join('x' if i in losses else ' ' for i in range(len(ref)))
    else:
        print_char = partial(_print_actual_expected_char, char='x', actual=losses,
                             expected=expected_losses)
        loss_str = ' '.join(print_char(i) for i in range(len(ref)))
    print(f'{"losses".rjust(left_col_width)} | {loss_str}')


def _print_reorders(ref: List[int],
                    reorders: Dict[int, int],
                    expected_reorders: Dict[int, int] = None):
    def print_(title: str, r: Dict[int, int]):
        reorder_str = ' '.join(str(r.get(i, ' ')) for i in range(len(ref)))
        print(f'{title.rjust(left_col_width)} | {reorder_str}')

    print_('delay', reorders)
    if expected_reorders is not None:
        print_('GT delay', expected_reorders)
