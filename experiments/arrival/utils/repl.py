from functools import partial
from typing import Callable, List

from generator.sequence import generate_random_sequence
from simulator.duplication import ar1_duplication
from simulator.loss import ge_loss
from simulator.random_process.state_machine import ge_configurations
from simulator.reordering import ar1_fixed_delay
from synchronizer.max_flow.alignment import Alignment
from synchronizer.max_flow.find_events import find_events, print_events
from synchronizer.max_flow.max_flow import max_flow_synchronzier
from utils.sample_test_signal import TestSignal, sample_test_signal


# TODO: Return the results and use for experiments, replace evaluate.py
def repl(get_test_signal: Callable[[], TestSignal] = None,
         synchronizer: Callable[[List[int], List[int]], List[Alignment]] = None,
         debug_print: Callable[[TestSignal, Alignment], None] = None):
    while True:
        test_signal = get_test_signal()
        alignments = synchronizer(test_signal.signal, test_signal.reference)
        print(f'FOUND {len(alignments)} ALIGNMENT{"S" if len(alignments) > 1 else ""}:\n')
        for alignment in alignments:
            debug_print(test_signal, alignment)
        input('Press Enter to continue...\n')


if __name__ == '__main__':
    loss_policy = partial(ge_loss, **ge_configurations[0.1])
    delay_policy = partial(ar1_fixed_delay, delay=2, prob=0.1)
    dupes_policy = partial(ar1_duplication, prob=0.1)

    policies = [loss_policy, delay_policy, dupes_policy]

    sample_2_bit_test_signal = partial(sample_test_signal,
                                       generator=generate_random_sequence(2),
                                       policies=policies,
                                       sent_packets=20,
                                       reference_length=50)


    def debug_print_events(test_signal: TestSignal, alignment: Alignment):
        sig, ref, perm = test_signal
        # TODO: Get expected events
        print_events(sig, ref, alignment, find_events(sig, alignment))


    max_flow_repl = partial(repl,
                            get_test_signal=sample_2_bit_test_signal,
                            synchronizer=partial(max_flow_synchronzier, margin=3, k=1),
                            debug_print=debug_print_events)

    max_flow_repl()
