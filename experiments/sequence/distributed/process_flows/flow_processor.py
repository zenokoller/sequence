from functools import partial
from typing import Callable

from process_flows.acquire_synch import acquire_synch
from process_flows.derive_events import derive_events


# TODO: Define signatures
def flow_processor(seed: int,
                   acquire_synch: Callable = None,
                   derive_events: Callable = None,
                   writer: Callable = None):
    while True:
        symbol = yield
        writer(symbol)
    # TODO: Magic


default_flow_processor = partial(flow_processor,
                                 acquire_synch=acquire_synch,
                                 derive_events=derive_events,
                                 writer=lambda x: print(x))
