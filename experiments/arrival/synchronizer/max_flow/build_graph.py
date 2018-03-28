from functools import partial
from typing import List, Tuple

import networkx as nx

from utils.range import matching_ranges, tuple_to_range

DEFAULT_MARGIN = 3
DEFAULT_DISPLACEMENT_RANGE = (-3, 4)
DEFAULT_DELAY_PENALTY = 2
DEFAULT_DISCRETIZE_FACTOR = 50


def build_graph(sig: List[int],
                ref: List[int],
                offset: int,
                margin: int = None,
                displacement_range: Tuple[int, int] = None,
                delay_penalty: int = None,
                discretize_factor: int = None) -> nx.DiGraph:
    graph = nx.DiGraph()
    ref_range = range(max(0, offset - margin), min(len(ref), offset + len(sig) + margin))

    _add_source_sink(graph, ref_range, sig)

    def displaced_range_starts(d: int) -> Tuple[int, int]:
        r0 = max(0, offset - margin, offset + d)
        s0 = r0 - d - offset
        return s0, r0

    def edge_weight(displacement: int, range_length: int) -> int:
        p = delay_penalty if displacement < 0 else 1
        return p * int(discretize_factor * (1 + abs(displacement)) / range_length)

    def add_edges_with_displacement(d: int):
        s0, r0 = displaced_range_starts(d)
        for lower, upper in matching_ranges(sig[s0:], ref[r0:]):
            weight = edge_weight(d, upper - lower)
            graph.add_edges_from((f's{s0 + i}', f'r{r0 + i}', {'capacity': 1, 'weight': weight})
                                 for i in range(lower, upper))

    for d in tuple_to_range(displacement_range):
        add_edges_with_displacement(d)

    return graph


def _add_source_sink(graph, ref_range, sig):
    graph.add_nodes_from(['S', 'T'])
    graph.add_nodes_from([f's{i}' for i in range(len(sig))])
    graph.add_nodes_from([f'r{i}' for i in ref_range])
    graph.add_edges_from(('S', f's{i}', {'capacity': 1, 'weight': 0}) for i in range(len(sig)))
    graph.add_edges_from((f'r{i}', 'T', {'capacity': 1, 'weight': 0}) for i in ref_range)


default_build_graph = partial(build_graph,
                              margin=DEFAULT_MARGIN,
                              displacement_range=DEFAULT_DISPLACEMENT_RANGE,
                              delay_penalty=DEFAULT_DELAY_PENALTY,
                              discretize_factor=DEFAULT_DISCRETIZE_FACTOR)
