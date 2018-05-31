import time


def nanosecond_timestamp() -> int:
    """Helper function that returns a timestamp in fake nanosecond resolution.
    Obsolete with `time.time_ns()` in python 3.7"""
    return int(round(time.time() * 1e09))
