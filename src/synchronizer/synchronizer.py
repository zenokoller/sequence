from asyncio import Queue
from typing import Callable

from synchronizer.states import configure_states


def get_synchronize_fn(**kwargs) -> Callable:
    initial_state_cls = configure_states(**kwargs)

    async def synchronize(seed: int, symbol_queue: Queue, event_queue: Queue,
                          sequence_cls: Callable):
        state = initial_state_cls(sequence_cls(seed))
        while True:
            symbol = await symbol_queue.get()
            state, event = await state.next(symbol)
            if event is not None:
                await event_queue.put(event)

    return synchronize


default_synchronize_args = {
    'initial_sync_confidence': 10,
    'recovery_batch_size': 25,
    'recovery_range_length': 250,
    'recovery_min_match_size': 15,
    'recovery_backoff_thresh': 10,
    'searching_batch_size': 50,
    'searching_min_match_size': 25,
    'searching_backoff_thresh': 5
}
