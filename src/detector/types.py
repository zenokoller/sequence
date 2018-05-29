from array import array
from typing import NamedTuple

Symbol = NamedTuple('Symbol', [('symbol', int), ('offset', int)])
Symbols = NamedTuple('Symbols', [('symbols', array), ('offset', int)])
ActualExpected = NamedTuple('ActualExpected', [
    ('actual', Symbols),
    ('expected', Symbols),
])
