from array import array
from typing import NamedTuple, Tuple

from utils.nanotime import nanosecond_timestamp


class Event:
    __slots__ = ('timestamp',)

    def __init__(self, *args, **kwargs):
        self.timestamp = nanosecond_timestamp()
        values = args if args else kwargs.values()
        for slot, value in zip(self.__slots__[1:], values):
            setattr(self, slot, value)

    def __iter__(self):
        return iter((getattr(self, slot) for slot in self.__slots__))

    def __repr__(self):
        attributes = ', '.join(str(getattr(self, slot)) for slot in self.__slots__[1:])
        return f'{self.__class__.__name__}({attributes})'


def make_event_type(typename: str, fields=Tuple[str]):
    slots = Event.__slots__ + fields
    return type(typename, (Event,), {'__slots__': slots})


Receive = make_event_type('Receive', ('offset',))
Loss = make_event_type('Loss', ('offset', 'size', 'found_offset'))
Delay = make_event_type('Delay', ('offset', 'amount'))

Symbol = NamedTuple('Symbol', [('symbol', int), ('offset', int)])
Symbols = NamedTuple('Symbols', [('symbols', array), ('offset', int)])
ActualExpected = NamedTuple('ActualExpected', [
    ('actual', Symbols),
    ('expected', Symbols),
])
