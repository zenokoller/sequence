import numpy as np

RECEIVED_COL = 1
SEQUENCE_COL = 2


def read_losses_from_csv(path: str, col: int, max_length: int = None) -> np.array:
    losses = np.genfromtxt(path, delimiter=',', dtype=int, skip_header=True)[:, col]
    return losses[:max_length].reshape(-1, 1)
