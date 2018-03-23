from typing import Callable, List

from synchronizer.max_flow.alignment import Alignment
from utils.sample_test_signal import TestSignal


# TODO: Return the results and use for experiments, replace evaluate.py
def repl(get_test_signal: Callable[[], TestSignal] = None,
         synchronizer: Callable[[List[int], List[int]], List[Alignment]] = None,
         debug_print: Callable[[TestSignal, List[Alignment]], None] = None,
         max_repeats: int = None):
    repeats = 0
    while max_repeats is None or repeats <= max_repeats:
        test_signal = get_test_signal()
        alignment = synchronizer(test_signal.signal, test_signal.reference)
        if callable(debug_print):
            debug_print(test_signal, alignment)
        repeats += 1
