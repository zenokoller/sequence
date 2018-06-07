import re
from typing import NamedTuple, Optional

NETEM_GE_RE = 'loss gemodel p (\d*\.?\d+)% r (\d*\.?\d+)% 1-h (\d*\.?\d+)% 1-k (\d*\.?\d+)%'
NETEM_FORMAT = '{:.1f} {:.0f} {:.0f} {:0.1f}'


class GEParams(NamedTuple):
    p: float = 0
    r: float = 1
    h: float = 1
    k: float = 0

    @classmethod
    def from_hmm(cls, model) -> 'GEParams':
        p, r = model.transmat_[0, 1], model.transmat_[1, 0]
        h, k = model.emissionprob_[1, 0], model.emissionprob_[0, 0]
        return GEParams(p, r, h, k)

    @classmethod
    def from_file(cls, path) -> Optional['GEParams']:
        """Parses file, returns first ge params it finds or None."""
        with open(path) as netem_file:
            return cls.from_str(netem_file.read())

    @classmethod
    def from_str(cls, string) -> Optional['GEParams']:
        """Parses file, returns first ge params it finds or None."""
        pattern = re.compile(NETEM_GE_RE, re.MULTILINE)
        match = pattern.search(string)
        if match is not None:
            def adjust(value, name) -> float:
                value = float(value) / 100
                return 1.0 - value if name in ['h', 'k'] else value

            return GEParams(
                *(adjust(value, name) for name, value in zip(['p', 'r', 'h', 'k'], match.groups())))
        else:
            return None

    def netem_format(self) -> str:
        return NETEM_FORMAT.format(
            *map(lambda x: x * 100, [self.p, self.r, (1 - self.h), (1 - self.k)]))

    def to_dict(self) -> dict:
        return {'p': self.p, 'r': self.r, 'h': self.h, 'k': self.k}
