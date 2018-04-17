from typing import List, Optional, NamedTuple, Callable, Any

from synchronizer.max_flow.build_graph import sig_node, node_to_index


class Alignment(NamedTuple):
    """For alignment indices a, if a[i] is None then the i-th signal symbol is
    unaccounted for. Otherwise, a[i] is the index of the reference position"""
    offset: int
    indices: List[Optional[int]]

    @classmethod
    def from_flow(cls, flow: dict, sig_length: int = None, offset: int = None) -> 'Alignment':
        assert offset is not None, 'Alignment needs an offset, None given.'
        indices = flow_to_indices(flow, sig_length=sig_length)
        return cls(offset=offset, indices=indices)


def flow_to_indices(flow: dict, sig_length: int = None) -> List[Optional[int]]:
    connections = {src: first_key_or_default(values, lambda x: x == 1, None)
                   for src, values in flow.items()}
    alignment_nodes = [connections.get(sig_node(i), None) for i in range(sig_length)]
    return [node_to_index(node) if node is not None else None for node in alignment_nodes]


def first_key_or_default(d: dict, condition: Callable[[Any], bool], default):
    try:
        return next(key for key, value in d.items() if condition(value))
    except StopIteration:
        return default
