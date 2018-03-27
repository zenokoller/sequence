from functools import partial

from estimator.print_events import print_events
from generator.sequence import generate_random_sequence
from simulator.ground_truth.predefined import predefined_policies
from simulator.policy import policies_str
from synchronizer.alignment import Alignment
from synchronizer.max_flow.build_graph import default_build_graph
from synchronizer.max_flow.max_flow import max_flow_synchronzier
from utils.eval_loop import eval_loop
from utils.sample import sample_uniform
from utils.test_signal import TestSignal

symbol_bits = 4


def sample_signal_lengths():
    return sample_uniform(5, 20), 30


policies = predefined_policies['medium']

generate_random_test_signal = partial(TestSignal.generate,
                                      generator=generate_random_sequence(symbol_bits),
                                      policies=policies,
                                      sample_signal_lengths=sample_signal_lengths)


def debug_print_events(test_signal: TestSignal, alignment: Alignment):
    sig, ref, ground_truth = test_signal
    print_events(sig, ref, alignment, ground_truth=ground_truth, symbol_bits=symbol_bits)
    input('\nPress Enter to run again...\n')
    # TODO: Make printing work for more symbol_bits

k = 3
synchronizer = partial(max_flow_synchronzier, build_graph=default_build_graph, k=k)

max_flow_repl = partial(eval_loop,
                        generate_test_signal=generate_random_test_signal,
                        synchronizer=synchronizer,
                        postprocess=debug_print_events)

print('Policies:\n', policies_str(policies), '\n')
print(f'Synchronizer: max_flow_synchronizer\n\tsymbol_bits: {symbol_bits}\n\t'
      f'hypotheses: {k}\n')
repl = max_flow_repl()
while True:
    next(repl)


