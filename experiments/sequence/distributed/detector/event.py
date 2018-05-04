from typing import List, Tuple, Union, NamedTuple

Loss = NamedTuple('Loss', [('offset', int), ('size', int)])
Delay = NamedTuple('Delay', [('offset', int), ('deyay', int)])
Duplicate = NamedTuple('Duplicate', [('offset', int)])
# TODO: Add timing information

Event = Union[Loss, Delay, Duplicate]
Events = List[Event]
