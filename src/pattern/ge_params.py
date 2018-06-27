import re
from math import isnan
from typing import NamedTuple, Optional, Dict

NETEM_GE_RE = 'loss gemodel p (\d*\.?\d+)% r (\d*\.?\d+)% 1-h (\d*\.?\d+)% 1-k (\d*\.?\d+)%'
PERCENT_STR_FORMAT = 'p: {:.2f}% r: {:.0f}% h: {:.0f}% k: {:0.3f}%'
NETEM_FORMAT = 'loss gemodel p {:.1f}% r {:.0f}% 1-h {:.0f}% 1-k {:0.3f}%'


class GEParams(NamedTuple):
    p: float = 0
    r: float = 1
    h: float = 1
    k: float = 1

    @classmethod
    def from_hmm(cls, model) -> 'GEParams':
        p, r = model.transmat_[0, 1], model.transmat_[1, 0]
        h, k = model.emissionprob_[1, 0], model.emissionprob_[0, 0]
        return GEParams(*[value if not isnan(value) else default
                          for value, default in zip([p, r, h, k], [0, 1, 1, 1])])

    @classmethod
    def from_file(cls, path) -> Optional['GEParams']:
        """Parses file, returns first ge params it finds or None."""
        with open(path) as netem_file:
            return cls.from_netem_str(netem_file.read())

    @classmethod
    def from_netem_str(cls, string) -> Optional['GEParams']:
        pattern = re.compile(NETEM_GE_RE, re.MULTILINE)
        match = pattern.search(string)
        if match is not None:
            def adjust(value, name) -> float:
                value = float(value) / 100
                return 1.0 - value if name in ['h', 'k'] else value

            return GEParams(
                *(adjust(value, name) for name, value in zip(['p', 'r', 'h', 'k'], match.groups())))
        else:
            return GEParams()

    def to_netem_str(self) -> str:
        return NETEM_FORMAT.format(
            *map(lambda x: x * 100, [self.p, self.r, (1 - self.h), (1 - self.k)]))

    def to_dict(self) -> Dict[str, float]:
        return {'p': self.p, 'r': self.r, 'h': self.h, 'k': self.k}
