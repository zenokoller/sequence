from typing import Optional

from estimator.events import Events
from estimator.find_events import find_events, find_losses
from simulator.ground_truth.ground_truth import GroundTruth
from synchronizer.alignment import Alignment


def loss_precision(alignment: Alignment, ground_truth: GroundTruth) -> float:
    """`Precision` measure for an alignment, which only considers losses. Yields -1 if there were no
    losses at all."""
    losses = find_losses(alignment)
    true_positives = len(set(losses).intersection(set(ground_truth.losses)))
    total_events = len(losses)
    return true_positives / total_events if total_events > 0 else -1
