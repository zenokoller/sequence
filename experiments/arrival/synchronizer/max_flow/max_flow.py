from itertools import product
from operator import itemgetter
from typing import List, Callable

import networkx as nx

from synchronizer.max_flow.alignment import Alignment
from synchronizer.max_flow.find_events import find_events, print_events


def max_flow_synchronzier(sig: List[int], ref: List[int], margin: int = None) -> List[Alignment]:
    offsets = top_k_offsets(sig, ref, k=1)
    return list(synch_at(offset, sig, ref, margin=margin) for offset in offsets)


def top_k_offsets(sig: List[int], ref: List[int], k: int = None) -> List[int]:
    exact_matches = [sum(s == r for s, r in zip(sig, ref[offset:]))
                     for offset in range(0, len(ref) - len(sig))]
    return [offset for offset, _ in sorted(enumerate(exact_matches), key=itemgetter(1))[-k:]]


def synch_at(offset: int, sig: List[int], ref: List[int], margin: int = None) -> Alignment:
    graph = build_graph(sig, ref, offset, margin)
    min_cost_flow = nx.max_flow_min_cost(graph, 'S', 'T')
    return alignment_from(min_cost_flow, length=len(sig))


def build_graph(sig: List[int], ref: List[int], offset: int, margin: int) -> nx.DiGraph:
    graph = nx.DiGraph()
    ref_range = range(max(0, offset - margin), min(len(ref), offset + len(sig) + margin))

    graph.add_nodes_from(['S', 'T'])
    graph.add_nodes_from([f's{i}' for i in range(len(sig))])
    graph.add_nodes_from([f'r{i}' for i in ref_range])

    graph.add_edges_from(('S', f's{i}', {'capacity': 1, 'weight': 0}) for i in range(len(sig)))
    graph.add_edges_from((f'r{i}', 'T', {'capacity': 1, 'weight': 0}) for i in ref_range)
    graph.add_edges_from(
        (f's{i}', f'r{j}', {'capacity': 1, 'weight': 1 / 1 + abs(j - i - offset)})
        for (i, s), j in product(enumerate(sig), ref_range)
        if s == ref[j])

    return graph


def alignment_from(flow: dict, length: int = None) -> Alignment:
    connections = {src: first_key(values, lambda x: x == 1, None)
                   for src, values in flow.items()}
    alignment_nodes = [connections.get(f's{i}', None) for i in range(length)]
    return [int(node[1:]) if node is not None else None for node in alignment_nodes]


def first_key(d: dict, condition: Callable, default):
    try:
        return next(key for key, value in d.items() if condition(value))
    except StopIteration:
        return default


sig = [1, 2, 5, 4, 7, 2, 1, 2]
ref = [3, 1, 2, 7, 5, 4, 2, 2, 2, 1, 2]
for alignment in max_flow_synchronzier(sig, ref, margin=3):
    print(alignment)
    lost, reordered, duped = find_events(alignment, sig)
    print_events(alignment, sig, ref, (lost, reordered, duped))

