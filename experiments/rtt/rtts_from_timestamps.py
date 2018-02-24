from typing import Tuple, Dict, List

import pandas as pd

from .rtt import RTT


def rtts_from_flow(flow: Tuple[str, pd.DataFrame]) -> pd.DataFrame:
    flow_hash, packets_df = flow

    rtts: List[RTT] = []
    observations: Dict[int, pd.Timestamp] = {}
    associations: Dict[int, int] = {}

    for packet in packets_df.itertuples():
        ts_val, ts_ecr = packet.ts_val, packet.ts_ecr
        if ts_val not in observations:
            observations[ts_val] = packet.timestamp
        if ts_ecr in observations:
            associations[ts_val] = ts_ecr
        associated = associations.get(ts_ecr, None)
        if associated is not None:
            rtts.append(RTT(timestamp=packet.timestamp,
                            flow_hash=flow_hash,
                            rtt=packet.timestamp - observations[associated]))
            del observations[associated]
            del associations[ts_ecr]

    return pd.DataFrame(rtts, columns=RTT._fields)
