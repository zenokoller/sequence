from typing import NamedTuple, Optional

from synchronizer.range_matcher.range import Range

Match = NamedTuple("Match", [('ref', Range), ('sig', Optional[Range])])
