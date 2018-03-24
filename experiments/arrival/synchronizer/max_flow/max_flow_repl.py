from functools import partial
from random import Random

from generator.sequence import generate_random_sequence
from simulator.duplication import ar1_duplication
from simulator.loss import ge_loss
from simulator.policy import policies_str
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


symbol_bits = 2
sample_random_test_signal = partial(sample_test_signal,
                                    generator=generate_random_sequence(symbol_bits),
                                    policies=policies,
                                    sample_signal_lengths=sample_signal_lengths)


def debug_print_events(test_signal: TestSignal, alignment: Alignment):
    sig, ref, perm = test_signal
    print_events(sig, ref, alignment, expected_alignment=test_signal.expected_alignment)
    input('\nPress Enter to run again...\n')


margin, k = 3, 3

max_flow_repl = partial(eval_loop,
                        get_test_signal=sample_random_test_signal,
                        synchronizer=partial(max_flow_synchronzier, margin=margin, k=k),
                        postprocess=debug_print_events)

print('Policies:\n', policies_str(policies), '\n')
print(f'Synchronizer: max_flow_synchronizer\n\tsymbol_bits: {symbol_bits}\n\tmargin: {margin}\n\t'
      f'hypotheses: {k}\n')
repl = max_flow_repl()
while True:
    next(repl)
