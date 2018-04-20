from process_flows.coroutine import coroutine


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
