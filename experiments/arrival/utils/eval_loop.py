from typing import Callable, List, Iterable, Any

from synchronizer.max_flow.alignment import Alignment
from utils.test_signal import TestSignal


def eval_loop(get_test_signal: Callable[[], TestSignal] = None,
              synchronizer: Callable[[List[int], List[int]], List[Alignment]] = None,
              postprocess: Callable[[TestSignal, List[Alignment]], Any] = None,
              max_repeats: int = None) -> Iterable[Any]:
    repeats = 0
    while max_repeats is None or repeats <= max_repeats:
        test_signal = get_test_signal()
        alignment = synchronizer(test_signal.signal, test_signal.reference)
        if callable(postprocess):
            yield postprocess(test_signal, alignment)
        repeats += 1

# TODO: Return the results and use for experiments
# Consider adding the original alignment to `TestSignal`
# Test with experiment
