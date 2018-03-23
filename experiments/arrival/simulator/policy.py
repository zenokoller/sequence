from functools import partial
from typing import Callable, Iterable, List

"""A function that takes an iterable, applies a policy (loss, reordering or duplication) and 
returns the result as an iterable."""
Policy = Callable[[Iterable], Iterable]


def policies_str(policies: List[Policy]) -> str:
    return '  ▶  '.join(policy_str(p) for p in policies)


def policy_str(policy: Policy) -> str:
    assert isinstance(policy, partial), 'Expected `functools.partial` instance.'
    func_name = str(policy.func).split(" ")[1]
    params = ', '.join(f'{k}={v}' for k, v in policy.keywords.items())
    return f'{func_name}({params})'
