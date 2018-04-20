import numpy as np

from utils.coroutine import coroutine


@coroutine
def start_search(first_symbol: int, batch_size: int = 50):
    buffer = np.zeros(batch_size, type=np.uint8)
    # TODO: Yield symbols and add to buffer as bytes (see `buffer_bytes`)
    # Once the batch is full, start a worker routine (concurrent.future, asyncio.ensure_future)
    # that tries to find the position.
    raise NotImplementedError('NIY: start_search')


@coroutine
def buffer_bytes(buffer: bytearray, first_symbol: int):
    initial = [first_symbol]
    while len(initial) < 4:
        initial.append((yield))
    byte = int(''.join([bin(x)[2:].rjust(2, '0') for x in initial]), 2)
    buffer.extend([byte])
    while True:
        try:
            byte = ((byte << 2) & 0xff) | (yield)
        except GeneratorExit:
            return
        buffer.extend([byte])
