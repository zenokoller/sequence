from functools import partial
from operator import itemgetter
from typing import List, Callable, Tuple, Iterable, NamedTuple

import networkx as nx

from estimator.print_events import print_events
from synchronizer.alignment import Alignment
from synchronizer.max_flow.build_graph import default_build_graph, SOURCE_NODE, SINK_NODE


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
    """Returns the k offsets of `sig` in `ref` that have the highest number of matching symbols."""
    exact_matches = (sum(s == r for s, r in zip(sig, ref[offset:]))
                     for offset in range(0, len(ref) - len(sig) + 1))
    return [offset for offset, _ in sorted(enumerate(exact_matches), key=itemgetter(1))[-k:]]


MaxFlowResult = NamedTuple('MaxFlowResult', [
    ('alignment', Alignment),
    ('cost', int),
    ('flow', int)])


def _synchronize(sig: List[int],
                 ref: List[int],
                 build_graph: Callable,
                 offset: int) -> MaxFlowResult:
    """Returns the the alignment and the cost of it."""
    graph = build_graph(sig, ref, offset)
    min_cost_flow = nx.max_flow_min_cost(graph, SOURCE_NODE, SINK_NODE)
    cost = nx.cost_of_flow(graph, min_cost_flow)
    flow = sum(min_cost_flow[SOURCE_NODE].values())
    alignment = Alignment.from_flow(min_cost_flow,
                                    sig_length=len(sig),
                                    offset=offset)
    return MaxFlowResult(alignment=alignment, cost=cost, flow=flow)


def choose_best(results: Iterable[MaxFlowResult]) -> Alignment:
    scored_alignments = (score_result(result) for result in results)
    return sorted(scored_alignments, key=itemgetter(1))[0][0]


UNMATCHED_PENALTY = 100


def score_result(result: MaxFlowResult) -> Tuple[Alignment, int]:
    alignment, cost, flow = result
    num_unmatched = len(alignment) - flow
    return alignment, cost + UNMATCHED_PENALTY * num_unmatched


default_max_flow_synchronizer = partial(max_flow_synchronzier,
                                        build_graph=default_build_graph,
                                        k=3)

if __name__ == '__main__':
    signal = [0, 1, 1, 2, 2, 3]
    reference = [3, 0, 1, 2, 1, 2, 2, 3, 4]

    alignment = max_flow_synchronzier(signal, reference, default_build_graph, k=3)
    print_events(signal, reference, alignment)
