from typing import Tuple, Dict, List, Set

import pandas as pd

from .rtt import RTT


def rtts_from_flow(flow: Tuple[str, pd.DataFrame]) -> pd.DataFrame:
    flow_hash, packets_df = flow

    rtts: List[RTT] = []
    observations: Dict[int, pd.Timestamp] = {}  # When was ts_val first seen?
    associations: Dict[int, pd.Timestamp] = {}  # When was the associated ts_val of echo first seen?
    seen_echos: Set[int] = {0}  # Only consider first echo to prevent overestimation

    def record_observation(val: int, observer_timestamp: pd.Timestamp):
        if val not in observations:
            observations[val] = observer_timestamp

    def make_association(value: int, echo: int):
        if echo in observations and echo not in seen_echos:
            associations[value] = observations[echo]
            seen_echos.add(echo)

    def record_rtt(echo: int, observer_timestamp: pd.Timestamp):
        associated = associations.get(echo, None)
        if associated is not None:
            rtts.append(RTT(timestamp=observer_timestamp,
                            flow_hash=flow_hash,
                            rtt=observer_timestamp - associated))
            del associations[echo]

    for packet in packets_df.itertuples():
        ts_val, ts_ecr, timestamp = packet.ts_val, packet.ts_ecr, packet.timestamp

        record_observation(ts_val, timestamp)
        make_association(ts_val, ts_ecr)
        record_rtt(ts_ecr, timestamp)

    return pd.DataFrame(rtts, columns=RTT._fields)
