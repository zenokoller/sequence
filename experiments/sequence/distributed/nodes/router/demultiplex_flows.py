import asyncio
import logging
from typing import Callable, Dict

import aioprocessing

from detector.detector import detector
from reporter.reporter import Reporter
from synchronizer.synchronizer import synchronize
from utils.types import FlowId


def get_demultiplex_flow_fn(seed_from_flow_id: Callable,
                            sequence_cls: Callable,
                            reporter: Reporter) -> Callable:
    def start_sync_and_detector(flow_id) -> asyncio.Queue:
        seed = seed_from_flow_id(*flow_id)
        logging.info(f'Start observing flow; flow_id={flow_id}; seed={seed}')
        symbol_queue, event_queue = asyncio.Queue(), asyncio.Queue()
        _ = asyncio.ensure_future(synchronize(seed, symbol_queue, event_queue, sequence_cls))
        _ = asyncio.ensure_future(detector(seed, event_queue, sequence_cls, reporter))
        return symbol_queue

    async def demultiplex_flows(in_queue: aioprocessing.Queue):
        out_queues: Dict[FlowId:asyncio.Queue] = {}

        while True:
            flow_id, symbol, time = await in_queue.coro_get()
            out_queue = out_queues.get(flow_id, None)
            if out_queue is None:
                out_queue = start_sync_and_detector(flow_id)
                out_queues[flow_id] = out_queue

            await out_queue.put(symbol)

    return demultiplex_flows
