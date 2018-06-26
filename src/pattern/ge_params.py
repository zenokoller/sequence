import re
from typing import NamedTuple, Optional, Dict

PERCENT_STR_RE = 'p:(\d*\.?\d+)% r:(\d*\.?\d+)% h:(\d*\.?\d+)% k:(\d*\.?\d+)%'
NETEM_GE_RE = 'loss gemodel p (\d*\.?\d+)% r (\d*\.?\d+)% 1-h (\d*\.?\d+)% 1-k (\d*\.?\d+)%'
PERCENT_STR_FORMAT = 'p {:.1f}% r {:.0f}% 1-h {:.0f}% 1-k {:0.3f}%'
NETEM_FORMAT = 'loss gemodel p {:.1f}% r {:.0f}% 1-h {:.0f}% 1-k {:0.3f}%'


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

    @classmethod
    def from_percent_str(cls, string) -> Optional['GEParams']:
        pattern = re.compile(PERCENT_STR_RE)
        match = pattern.search(string)
        if match is not None:
            # return GEParams(
            #     *map(lambda x: x / 100, match.groups())
            # )

            def adjust(value, name) -> float:
                value = float(value) / 100
                value = min(1., max(0., value))
                return 1.0 - value if name in ['h', 'k'] else value

            return GEParams(
                *(adjust(value, name) for name, value in zip(['p', 'r', 'h', 'k'], match.groups())))
        else:
            return GEParams()

    def to_percent_str(self) -> str:
        return PERCENT_STR_FORMAT.format(*self)

    def to_netem_str(self) -> str:
        return NETEM_FORMAT.format(
            *map(lambda x: x * 100, [self.p, self.r, (1 - self.h), (1 - self.k)]))

    def to_dict(self) -> Dict[str, float]:
        return {'p': self.p, 'r': self.r, 'h': self.h, 'k': self.k}

    def rel_errors(self, ground_truth: 'GEParams') -> Dict[str, float]:
        return {name: abs(x - gt) / gt if gt != 0 else 0
                for x, gt, name in zip(self, ground_truth, ['p', 'r', 'h', 'k'])}

def clip(value, min, max):
    return min(max, max(min, value))

