from functools import partial
from typing import List, Iterable

import itertools

import pandas as pd

from generator.sequence import generate_random_sequence
from simulator.loss import ar1_loss
from simulator.permutation import generate_permutation, apply_permutation
from simulator.simulator import Policy
from utils.consume import consume, consume_all
from synchronizer.find_losses import find_losses


def run_loss_finder(sequence: Iterable[int],
                    length: int,
                    policies: List[Policy]):
    original = consume(sequence, length=length)
    permutation = consume_all(generate_permutation(policies, length))
    received = apply_permutation(original, permutation)

    expected = find_losses(consume_all(range(length)), permutation)
    actual = find_losses(original, received)
    return expected, actual


ten_percent_loss = partial(ar1_loss, prob=0.1, corr=0.25)


def test_loss_finder():
    packets = [10, 25, 50, 100, 200]
    chunk_sizes = [1, 2, 4]
    correct_df = pd.DataFrame(index=packets, columns=chunk_sizes)
    loss_count_df = pd.DataFrame(index=packets, columns=chunk_sizes)
    for length, chunk_size in itertools.product(packets, chunk_sizes):
        sequence = generate_random_sequence(chunk_size, seed=42)
        expected, actual = run_loss_finder(sequence, length, [ten_percent_loss])
        correct_df.loc[length, chunk_size] = expected == actual
        loss_count_df.loc[length, chunk_size] = len(expected)
    print(correct_df)
    print(loss_count_df)


# TODO: Measure accuracy as a scalar

test_loss_finder()
