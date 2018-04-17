from functools import partial
from typing import List, Tuple, Callable

import networkx as nx

from synchronizer.max_flow.energy import edge_energy, default_edge_energy
from signal_utils.range import tuple_to_range
from signal_utils.common_subsequences import common_subsequences

SOURCE_NODE = 'S'
SINK_NODE = 'T'

DEFAULT_MARGIN = 3
DEFAULT_SHIFT_RANGE = (-5, 6)


def build_graph(sig: List[int],
                ref: List[int],
                offset: int,
                margin: int = None,
                shift_range: Tuple[int, int] = None,
                edge_weight: Callable[[int, int], int] = None) -> nx.DiGraph:
    graph = nx.DiGraph()
    ref_range = range(max(0, offset - margin), min(len(ref), offset + len(sig) + margin))

    _add_source_sink(graph, ref_range, sig)

    def shifted_sequence_starts(shift: int) -> Tuple[int, int]:
        r0 = max(0, offset - margin, offset + shift)
        s0 = r0 - shift - offset
        return s0, r0

    def add_shifted_edges(shift: int):
        s0, r0 = shifted_sequence_starts(shift)
        for lower, upper in common_subsequences(sig[s0:], ref[r0:]):
            weight = edge_weight(shift, upper - lower)
            graph.add_edges_from((sig_node(s0 + i), ref_node(r0 + i),
                                  {'capacity': 1, 'weight': weight}) for i in range(lower, upper))

    for shift in tuple_to_range(shift_range):
        add_shifted_edges(shift)

    return graph


def _add_source_sink(graph, ref_range, sig):
    graph.add_nodes_from([SOURCE_NODE, SINK_NODE])
    graph.add_nodes_from([sig_node(i) for i in range(len(sig))])
    graph.add_nodes_from([ref_node(i) for i in ref_range])
    graph.add_edges_from(
        (SOURCE_NODE, sig_node(i), {'capacity': 1, 'weight': 0}) for i in range(len(sig)))
    graph.add_edges_from((ref_node(i), SINK_NODE, {'capacity': 1, 'weight': 0}) for i in ref_range)


def sig_node(i: int) -> str:
    return f's{i}'


def ref_node(i: int) -> str:
    return f'r{i}'


def node_to_index(node: str) -> int:
    return int(node[1:])


default_build_graph = partial(build_graph,
                              margin=DEFAULT_MARGIN,
                              shift_range=DEFAULT_SHIFT_RANGE,
                              edge_weight=default_edge_energy)
