from functools import partial
from random import Random
from typing import List

from generator.sequence import generate_random_sequence
from simulator.duplication import ar1_duplication
from simulator.loss import ge_loss
from simulator.random_process.state_machine import ge_configurations
from simulator.reordering import ar1_fixed_delay
from synchronizer.max_flow.alignment import expected_alignment, Alignment
from synchronizer.max_flow.max_flow import max_flow_synchronzier
from synchronizer.max_flow.print_events import print_events
from utils.repl import repl
from utils.sample_test_signal import TestSignal, sample_test_signal

loss_policy = partial(ge_loss, **ge_configurations[0.02])
delay_policy = partial(ar1_fixed_delay, delay=2, prob=0.01)
dupes_policy = partial(ar1_duplication, prob=0.01)

policies = [loss_policy, delay_policy, dupes_policy]


def sample_signal_lengths():
    signal_length = Random().randint(5, 20)
    reference_length = 50
    return signal_length, reference_length


sample_2_bit_test_signal = partial(sample_test_signal,
                                   generator=generate_random_sequence(3),
                                   policies=policies,
                                   sample_signal_lengths=sample_signal_lengths)


def debug_print_events(test_signal: TestSignal, alignments: List[Alignment]):
    sig, ref, perm = test_signal
    print(f'FOUND {len(alignments)} ALIGNMENT{"S" if len(alignments) > 1 else ""}:\n')
    for alignment in alignments:
        print_events(sig, ref, alignment, expected_alignment=expected_alignment(test_signal))
        print('')
    input('Press Enter to continue...\n')


max_flow_repl = partial(repl,
                        get_test_signal=sample_2_bit_test_signal,
                        synchronizer=partial(max_flow_synchronzier, margin=3, k=1),
                        debug_print=debug_print_events)

max_flow_repl()
