import numpy as np


def strided(array: np.array, stride: int) -> np.array:
    """Allows iterating over the array in rows of size `stride` without copying."""
    num_chunks = ((array.size - stride) // stride) + 1
    strides = array.strides[0]
    return np.lib.stride_tricks.as_strided(array,
                                           shape=(num_chunks, stride),
                                           strides=(stride * strides, strides))
