from functools import partial

from simulator.ground_truth.duplication import ar1_duplication
from simulator.ground_truth.loss import ge_loss
from simulator.ground_truth.reordering import ar1_uniform_delay

_loss_rates = [0.01, 0.02, 0.05, 0.10]
_ge_confs = {
    key: {kw: param for kw, param in zip(
        ('move_to_bad',
         'move_to_good',
         'drop_in_bad',
         'drop_in_good'), conf)} for key, conf in
    zip(_loss_rates, [
        (0.005, 0.7, 0.5, 0.0075),  # 1% loss
        (0.01, 0.75, 0.8, 0.01),  # 2% loss
        (0.035, 0.75, 0.8, 0.02),  # 5% loss
        (0.075, 0.75, 0.8, 0.03),  # 10% loss
    ])}

normal_policies = [
    partial(ge_loss, **_ge_confs[0.01]),
    partial(ar1_uniform_delay, delay_bounds=(1, 5), prob=0.005),
    partial(ar1_duplication, prob=0.001)
]

medium_policies = [
    partial(ge_loss, **_ge_confs[0.02]),
    partial(ar1_uniform_delay, delay_bounds=(1, 5), prob=0.005),
    partial(ar1_duplication, prob=0.002)
]

high_policies = [
    partial(ge_loss, **_ge_confs[0.05]),
    partial(ar1_uniform_delay, delay_bounds=(1, 5), prob=0.01),
    partial(ar1_duplication, prob=0.005)
]

severe_policies = [
    partial(ge_loss, **_ge_confs[0.1]),
    partial(ar1_uniform_delay, delay_bounds=(1, 5), prob=0.05),
    partial(ar1_duplication, prob=0.01)
]

predefined_policies = {
    'normal': normal_policies,
    'medium': medium_policies,
    'high': high_policies,
    'severe': severe_policies
}
