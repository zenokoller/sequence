import numpy as np


def strided(array: np.array, chunk_size: int) -> np.array:
    """Allows iterating over the array in chunk_size rows without copying."""
    num_chunks = ((array.size - chunk_size) // chunk_size) + 1
    strides = array.strides[0]
    return np.lib.stride_tricks.as_strided(array,
                                           shape=(num_chunks, chunk_size),
                                           strides=(chunk_size * strides, strides))
