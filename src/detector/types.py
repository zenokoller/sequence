from array import array
from typing import NamedTuple

Symbol = NamedTuple('Symbol', [('symbol', int), ('seq_offset', int), ('buf_offset', int)])
Symbols = NamedTuple('Symbols', [('symbols', array), ('offset', int)])
ActualExpected = NamedTuple('ActualExpected', [
    ('actual', Symbols),
    ('expected', Symbols),
])
