from contextlib import contextmanager

import plt


@contextmanager
def managed_trace(in_uri):
    trace = plt.trace(in_uri)
    trace.start()
    try:
        yield trace
    finally:
        trace.close()


@contextmanager
def managed_output_trace(in_uri):
    trace = plt.output_trace(in_uri)
    trace.start_output()
    try:
        yield trace
    finally:
        trace.close_output()
