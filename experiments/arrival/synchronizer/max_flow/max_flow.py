from functools import partial
from operator import itemgetter
from typing import List, Callable, Tuple, Iterable, Optional

import networkx as nx

from synchronizer.max_flow.alignment import Alignment
from synchronizer.max_flow.build_graph import default_build_graph
from synchronizer.max_flow.print_events import print_events


def max_flow_synchronzier(sig: List[int],
                          ref: List[int],
                          build_graph: Callable = None,
                          k: int = 1) -> Alignment:
    """Computes the best guess of signal `sig` within reference `ref` using min cost max flow.
    `k` controls the number of hypotheses, `build_graph` produces the graph given `sig`,
    `ref` and an offset."""
    offsets = top_k_offsets(sig, ref, k)
    synch_at = partial(_synchronize, sig, ref, build_graph)
    return choose_best(
        synch_at(offset) for offset in offsets
    )


def top_k_offsets(sig: List[int], ref: List[int], k: int = None) -> List[int]:
    exact_matches = [sum(s == r for s, r in zip(sig, ref[offset:]))
                     for offset in range(0, len(ref) - len(sig))]
    return [offset for offset, _ in sorted(enumerate(exact_matches), key=itemgetter(1))[-k:]]


def _synchronize(sig: List[int],
                 ref: List[int],
                 build_graph: Callable,
                 offset: int) -> Tuple[Alignment, int]:
    """Returns the the alignment and the cost of it."""
    graph = build_graph(sig, ref, offset)
    min_cost_flow = nx.max_flow_min_cost(graph, 'S', 'T')
    cost = nx.cost_of_flow(graph, min_cost_flow)
    indices = _alignment_indices(min_cost_flow, length=len(sig))
    return Alignment(offset=offset, indices=indices), cost


def _alignment_indices(flow: dict, length: int = None) -> List[Optional[int]]:
    connections = {src: first_key(values, lambda x: x == 1, None)
                   for src, values in flow.items()}
    alignment_nodes = [connections.get(f's{i}', None) for i in range(length)]
    return [int(node[1:]) if node is not None else None for node in alignment_nodes]


def choose_best(alignments_costs: Iterable[Tuple[Alignment, int]]) -> Alignment:
    (best_offset, best_alignment), _ = sorted(alignments_costs, key=itemgetter(1))[0]
    return best_offset, best_alignment


def first_key(d: dict, condition: Callable, default):
    try:
        return next(key for key, value in d.items() if condition(value))
    except StopIteration:
        return default


if __name__ == '__main__':
    signal = [0, 1, 1, 2, 2, 3]
    reference = [3, 0, 1, 2, 1, 2, 2, 3, 4]

    alignment = max_flow_synchronzier(signal, reference, default_build_graph, k=3)
    print_events(signal, reference, alignment)
