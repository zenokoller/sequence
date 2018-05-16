import asyncio
import logging
from asyncio import Queue
from typing import Callable, Dict

from detector.detector import detector
from detector.event import Receive
from synchronizer.synchronizer import synchronize
from utils.integer_codec import decode_symbol_with_offset
from utils.types import Address


def get_server_protocol(seed_from_addr: Callable,
                        sequence_cls: Callable,
                        reporter_queue: Queue,
                        report_received: bool = False):
    class SequenceServerProtocol:
        def __init__(self, echo=False):
            self.echo = echo
            self.transport = None
            self.queues: Dict[Address: Queue] = {}

        def connection_made(self, transport):
            self.transport = transport

        def connection_lost(self, exc):
            if exc is not None:
                logging.warning(f'Connection lost: {exc}')

        def datagram_received(self, data, addr):
            queue = self.queues.get(addr, None)
            if queue is None:
                queue = self.start_sync_and_detector(addr)
                self.queues[addr] = queue

            symbol, offset = decode_symbol_with_offset(data)
            queue.put_nowait(symbol)

            if report_received:
                reporter_queue.put_nowait(Receive(offset))

            if self.echo:
                self.transport.sendto(data, addr)

        def start_sync_and_detector(self, addr) -> Queue:
            seed = seed_from_addr(addr)
            logging.info(f'Start observing flow; addr={addr}; seed={seed}')
            symbol_queue, event_queue = Queue(), Queue()
            _ = asyncio.ensure_future(synchronize(seed, symbol_queue, event_queue, sequence_cls))
            _ = asyncio.ensure_future(detector(seed, event_queue, reporter_queue, sequence_cls))
            return symbol_queue

    return SequenceServerProtocol
