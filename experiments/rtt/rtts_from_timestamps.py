from typing import Tuple, Dict, List, Set

import pandas as pd

from .rtt import RTT


def rtts_from_flow(flow: Tuple[str, pd.DataFrame]) -> pd.DataFrame:
    flow_hash, packets_df = flow

    rtts: List[RTT] = []
    observations: Dict[int, pd.Timestamp] = {}  # When was ts_val first seen?
    associations: Dict[int, pd.Timestamp] = {}  # When was the associated ts_val of echo first seen?
    seen_echos: Set[int] = {0}  # Only consider first echo to prevent overestimation

    for packet in packets_df.itertuples():
        ts_val, ts_ecr = packet.ts_val, packet.ts_ecr
        if ts_val not in observations:
            observations[ts_val] = packet.timestamp
        if ts_ecr in observations and ts_ecr not in seen_echos:
            associations[ts_val] = observations[ts_ecr]
            seen_echos.add(ts_ecr)
        associated = associations.get(ts_ecr, None)
        if associated is not None:
            rtts.append(RTT(timestamp=packet.timestamp,
                            flow_hash=flow_hash,
                            rtt=packet.timestamp - associated))
            del associations[ts_ecr]

    return pd.DataFrame(rtts, columns=RTT._fields)
