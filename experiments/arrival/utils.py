from typing import List

import numpy as np

from experiments.arrival.generator import Sequence


def consume_all(sequence: Sequence) -> List[int]:
    return [item for item in sequence]

