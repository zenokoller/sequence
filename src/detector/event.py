import time
from typing import Tuple, List


class Event:
    __slots__ = ('timestamp',)

    def __init__(self, *args, **kwargs):
        self.timestamp = int(time.time() * 1e09)  # [ns] UNIX time
        values = args if args else kwargs.values()
        for slot, value in zip(self.__slots__[1:], values):
            setattr(self, slot, value)

    def __iter__(self):
        return iter((getattr(self, slot) for slot in self.__slots__))


def make_event_type(typename: str, fields=Tuple[str]):
    slots = Event.__slots__ + fields
    return type(typename, (Event,), {'__slots__': slots})


Events = List[Event]

Receive = make_event_type('Receive', ('offset',))

Loss = make_event_type('Loss', ('offset', 'size', 'found_offset'))
Delay = make_event_type('Delay', ('offset', 'delay'))
Duplicate = make_event_type('Duplicate', ('offset',))
