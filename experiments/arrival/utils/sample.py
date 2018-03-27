from random import Random

import numpy as np


def sample_uniform(a: int, b: int) -> int:
    return Random().randint(a, b)


def sample_lognormal(mu: int, sigma: int) -> int:
    return int(np.random.lognormal(mu, sigma))
