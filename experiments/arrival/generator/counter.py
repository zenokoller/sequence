from typing import Iterable


def counter() -> Iterable[int]:
    count = 0
    while True:
        yield count
        count += 1
