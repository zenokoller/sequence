import operator
from array import array
from itertools import islice
from typing import NamedTuple, Tuple, Callable, Iterable

from utils.nanotime import nanosecond_timestamp


class Event:
    __slots__ = ('timestamp',)

    def __init__(self, *args, **kwargs):
        self.timestamp = nanosecond_timestamp()
        values = args if args else kwargs.values()
        for slot, value in zip(self.__slots__, values):
            setattr(self, slot, value)

    def __iter__(self):
        return iter((getter(self) for getter in self.getters))

    def __repr__(self):
        attributes = ', '.join(str(getter(self)) for getter in self.getters)
        return f'{self.__class__.__name__}({attributes})'

    def __eq__(self, other):
        if type(other) is type(self) and other.__slots__ == self.__slots__:
            return all(getter(self) == getter(other) for getter
                       in islice(self.getters, 0, len(self.__slots__) - 1))

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def getters(self) -> Iterable[Callable]:
        return (operator.attrgetter(attr) for attr in self.__slots__)


def make_event_type(typename: str, fields=Tuple[str]):
    slots = fields + Event.__slots__
    return type(typename, (Event,), {'__slots__': slots})


Receive = make_event_type('Receive', ('offset',))
Loss = make_event_type('Loss', ('offset', 'found_offset'))
Reordering = make_event_type('Reordering', ('offset', 'amount'))

Symbol = NamedTuple('Symbol', [('symbol', int), ('offset', int)])
Symbols = NamedTuple('Symbols', [('symbols', array), ('offset', int)])
ActualExpected = NamedTuple('ActualExpected', [
    ('actual', Symbols),
    ('expected', Symbols),
])