from random import Random
from typing import Callable, Tuple, List

from simulator.random_process.random_process import RandomProcess

StateFn = Callable[[], Tuple[bool, int]]


def state_machine(states: List[StateFn]) -> RandomProcess:
    """The `states` functions each represent a state. They return
    the next value drawn from the process the next state."""
    assert len(states) > 0, 'No states given'
    state = states[0]
    while True:
        draw, next_index = state()
        state = states[next_index]
        yield draw


def gilbert_elliot(move_to_bad=0.0,
                   move_to_good=None,
                   drop_in_bad=1.0,
                   drop_in_good=0.0,
                   seed: int = None) -> RandomProcess:
    """
    Loss model with two states, good and bad. `True` corresponds to a loss.
    - In the good state, a loss can still occur with `prob_loss_good`
    - In the bad state, a packet can still be transmitted with `prob_transmit_bad`.
    """
    r = Random(seed)

    move_to_good = move_to_good if move_to_good is not None else 1 - move_to_bad

    def good() -> Tuple[bool, int]:
        transition = r.random() < move_to_bad
        return (r.random() < drop_in_bad, 1) if transition \
            else (r.random() < drop_in_good, 0)

    def bad() -> Tuple[bool, int]:
        transition = r.random() < move_to_good
        return (r.random() < drop_in_good, 0) if transition \
            else (r.random() < drop_in_bad, 1)

    return state_machine([good, bad])


"""Some configurations for the GE model which yield the given net loss rates."""
loss_rates = [0.01, 0.02, 0.05, 0.10]
ge_configurations = {
    key: {kw: param for kw, param in zip(('move_to_bad', 'move_to_good', 'drop_in_bad',
                                          'drop_in_good'), conf)} for key, conf in zip(loss_rates, [
    (0.005, 0.7, 0.5, 0.0075),  # 1% loss
    (0.01, 0.75, 0.8, 0.01),    # 2% loss
    (0.035, 0.75, 0.8, 0.02),   # 5% loss
    (0.075, 0.75, 0.8, 0.03),   # 10% loss
])
}

# TODO: Implement GI model from below
# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.479.8782&rep=rep1&type=pdf
