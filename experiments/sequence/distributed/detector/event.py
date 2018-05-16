from typing import List, Union, NamedTuple

Receive = NamedTuple('Receive', [('offset', int)])

Loss = NamedTuple('Loss', [('offset', int), ('size', int), ('found_offset', int)])
Delay = NamedTuple('Delay', [('offset', int), ('deyay', int)])
Duplicate = NamedTuple('Duplicate', [('offset', int)])

Event = Union[Receive, Loss, Delay, Duplicate]
Events = List[Event]
