import time


def nanosecond_timestamp() -> int:
    return int(round(time.time() * 1e09))
