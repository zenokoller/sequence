from typing import Optional

from estimator.events import Events
from estimator.find_events import find_events
from simulator.ground_truth.ground_truth import GroundTruth
from synchronizer.alignment import Alignment


def precision(alignment: Alignment, ground_truth: GroundTruth) -> float:
    """`Precision` measure for an alignment. Yields -1 if there were no events at all."""
    events = find_events(alignment)
    true_positives = count_true_positives(events, ground_truth)
    total_events = events.number_of_events
    return true_positives / total_events if total_events > 0 else -1


def count_true_positives(events: Events, ground_truth: GroundTruth) -> int:
    losses, delays, dupes = events
    gt_losses, gt_delays, gt_dupes = ground_truth
    return len(set(losses).intersection(set(gt_losses))) + \
           len(set(dupes).intersection(set(gt_dupes))) + \
           len([key for key, value in delays.items() if value == gt_delays.get(key, None)])
