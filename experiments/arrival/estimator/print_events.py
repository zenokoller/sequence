from functools import partial
from typing import List, Dict

from termcolor import colored

from simulator.ground_truth.ground_truth import GroundTruth
from synchronizer.alignment import Alignment
from estimator.find_events import find_events

LABEL_WIDTH = 10
DIVIDER = ' '


def print_events(sig: List[int],
                 ref: List[int],
                 alignment: Alignment,
                 ground_truth: GroundTruth = None,
                 symbol_bits: int = 2):
    offset, _ = alignment
    losses, delays, dupes = find_events(alignment)
    exp_losses, exp_delays, exp_dupes = ground_truth if ground_truth is not None \
        else (None, None, None)

    symbol_width = len(str(2 ** symbol_bits))
    _print_dupes(sig, offset, dupes, exp_dupes, symbol_width)
    _print_signals(sig, ref, offset, symbol_width)
    _print_losses(ref, losses, exp_losses, symbol_width)
    _print_delays(ref, delays, exp_delays, symbol_width)


def _print_dupes(sig: List[int],
                 offset: int, dupes: List[int],
                 expected_dupes: List[int] = None,
                 symbol_width: int = 1):
    token = 'd'.rjust(symbol_width)
    space = ' ' * symbol_width
    if expected_dupes is None:
        dupes_str = ' '.join(token if i in dupes else space for i in range(len(sig)))
    else:
        print_token = partial(_print_actual_expected_token, token=token, actual=dupes,
                              expected=expected_dupes, symbol_width=symbol_width)
        dupes_str = ' '.join(print_token(i) for i in range(len(sig)))
    offset_str = _offset_str(offset, symbol_width=symbol_width)
    print(f'{"dupes".rjust(LABEL_WIDTH)} | {offset_str}{dupes_str}')


def _offset_str(offset: int, symbol_width: int = 1) -> str:
    if offset < 0:
        return ''
    else:
        return ' ' * (symbol_width + 1) * offset


def _print_actual_expected_token(i: int,
                                 token: str = None,
                                 actual: list = None,
                                 expected: list = None,
                                 symbol_width: int = 1) -> str:
    if i in actual and i in expected:
        return colored(token, 'green')
    elif i in actual:
        return colored(token, 'red')
    elif i in expected:
        return colored(token, 'blue')
    else:
        return ' ' * symbol_width


def _print_signals(sig: List[int],
                   ref: List[int],
                   offset: int,
                   symbol_width: int = 1):
    sig_offset = _offset_str(offset, symbol_width=symbol_width) if offset > 0 else ''
    sig_str = DIVIDER.join(str(s).rjust(symbol_width) for s in sig)
    print(f'{"SIGNAL".rjust(LABEL_WIDTH)} | {sig_offset}{sig_str}')

    ref_offset = _offset_str(abs(offset), symbol_width=symbol_width) if offset < 0 else ''
    ref_str = DIVIDER.join(str(r).rjust(symbol_width) for r in ref)
    print(f'{"REFERENCE".rjust(LABEL_WIDTH)} | {ref_offset}{ref_str}')


def _print_losses(ref: List[int],
                  losses: List[int],
                  expected_losses: List[int] = None,
                  symbol_width: int = 1):
    token = 'x'.rjust(symbol_width)
    space = ' ' * symbol_width
    if expected_losses is None:
        loss_str = ' '.join(token if i in losses else space for i in range(len(ref)))
    else:
        print_token = partial(_print_actual_expected_token, token=token, actual=losses,
                              expected=expected_losses, symbol_width=symbol_width)
        loss_str = ' '.join(print_token(i) for i in range(len(ref)))
    print(f'{"losses".rjust(LABEL_WIDTH)} | {loss_str}')


def _print_delays(ref: List[int],
                  reorders: Dict[int, int],
                  expected_reorders: Dict[int, int] = None,
                  symbol_width: int = 1):
    def print_(title: str, r: Dict[int, int]):
        reorder_str = ' '.join(str(r.get(i, ' ')).rjust(symbol_width) for i in range(len(ref)))
        print(f'{title.rjust(LABEL_WIDTH)} | {reorder_str}')

    print_('delay', reorders)
    if expected_reorders is not None:
        print_('GT delay', expected_reorders)
