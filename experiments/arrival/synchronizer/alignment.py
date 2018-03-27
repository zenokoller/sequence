from typing import List, Optional, NamedTuple

"""For alignment indices a, if a[i] is None then the i-th signal symbol is 
unaccounted for. Otherwise, a[i] is the index of the reference position"""
Alignment = NamedTuple('Alignment', [('offset', int), ('indices', List[Optional[int]])])
