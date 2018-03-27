from estimator.events import Events
from estimator.find_events import find_events
from simulator.ground_truth.ground_truth import GroundTruth
from synchronizer.max_flow.alignment import Alignment


def accuracy(alignment: Alignment, ground_truth: GroundTruth) -> float:
    events = find_events(alignment)
    num_correct = count_correctly_predicted(events, ground_truth)
    num_predicted = events.number_of_events
    num_wrong = num_predicted - num_correct
    return num_correct / ground_truth.number_of_events - num_wrong / num_predicted


def count_correctly_predicted(events: Events, ground_truth: GroundTruth) -> int:
    losses, delays, dupes = events
    gt_losses, gt_delays, gt_dupes = ground_truth
    return len(set(losses).intersection(set(gt_losses))) + \
           len(set(dupes).intersection(set(gt_dupes))) + \
           len([key for key, value in delays.items() if value == gt_delays.get(key, None)])
