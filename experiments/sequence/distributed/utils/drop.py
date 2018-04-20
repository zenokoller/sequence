import itertools


def drop(it, n):
    return itertools.islice(it, n, None)
