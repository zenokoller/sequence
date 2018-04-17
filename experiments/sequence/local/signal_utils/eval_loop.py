from typing import Callable, List, Iterable, Any

from synchronizer.alignment import Alignment
from signal_utils.test_signal import TestSignal


def eval_loop(generate_test_signal: Callable[[], TestSignal] = None,
              synchronizer: Callable[[List[int], List[int]], List[Alignment]] = None,
              postprocess: Callable[[TestSignal, List[Alignment]], Any] = None) -> Iterable[Any]:
    while True:
        test_signal = generate_test_signal()
        alignment = synchronizer(test_signal.signal, test_signal.reference)
        if callable(postprocess):
            yield postprocess(test_signal, alignment)
