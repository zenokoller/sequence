def pairwise(it):
    it = iter(it)
    while True:
        yield next(it), next(it)


def as_batches(iterable, batch_size=1):
    l = len(iterable)
    for index in range(0, l, batch_size):
        yield iterable[index:min(index + batch_size, l)]
