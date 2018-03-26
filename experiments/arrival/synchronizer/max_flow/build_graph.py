from typing import List, Iterable, Tuple

import networkx as nx

D = 3
DEFAULT_DELAY_PENALTY = 3
DEFAULT_DISCRETIZE_FACTOR = 50


def build_graph(sig: List[int], ref: List[int], offset: int, margin: int) -> nx.DiGraph:
    graph = nx.DiGraph()
    ref_range = range(max(0, offset - margin), min(len(ref), offset + len(sig) + margin))

    graph.add_nodes_from(['S', 'T'])
    graph.add_nodes_from([f's{i}' for i in range(len(sig))])
    graph.add_nodes_from([f'r{i}' for i in ref_range])

    graph.add_edges_from(('S', f's{i}', {'capacity': 1, 'weight': 0}) for i in range(len(sig)))
    graph.add_edges_from((f'r{i}', 'T', {'capacity': 1, 'weight': 0}) for i in ref_range)

    def displaced_range_starts(d: int) -> Tuple[int, int]:
        r0 = max(0, offset - margin, offset + d)
        s0 = r0 - d - offset
        return s0, r0

    def add_edges_with_displacement(d: int):
        s0, r0 = displaced_range_starts(d)
        for lower, upper in matching_ranges(sig[s0:], ref[r0:]):
            weight = _edge_weight(d, upper - lower)
            graph.add_edges_from((f's{s0 + i}', f'r{r0 + i}', {'capacity': 1, 'weight': weight})
                                 for i in range(lower, upper))

    for d in range(-D, D + 1):
        add_edges_with_displacement(d)

    return graph


def matching_ranges(first: Iterable[int],
                    second: Iterable[int]) -> Iterable[Tuple[int, int]]:
    """Given two lists `first` and `second`, yields bounds of matching subsequences."""
    start = None
    for i, (a, b) in enumerate(zip(first, second)):
        if a == b and start is None:
            start = i
        elif a != b and start is not None:
            yield (start, i)
            start = None

    if start is not None:
        yield (start, min(len(first), len(second)))
    return


def _edge_weight(displacement: int,
                 range_length: int,
                 delay_penalty: int = DEFAULT_DELAY_PENALTY,
                 discretize_factor: int = DEFAULT_DISCRETIZE_FACTOR) -> int:
    delay_penalty = delay_penalty if displacement < 0 else 1
    return delay_penalty * int(discretize_factor * (1 + abs(displacement)) / range_length)
