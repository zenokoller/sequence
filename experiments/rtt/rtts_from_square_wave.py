from collections import namedtuple
from typing import NamedTuple, Tuple, List

import pandas as pd

from .rtt import RTT


class DataPoint(NamedTuple):
    timestamp: pd.Timestamp
    spin_bit: bool


def signals_from_flow(packets_df: pd.DataFrame) -> Tuple[List[DataPoint], List[DataPoint]]:
    class Host():
        highest_ts_val: int = 0
        spin_bit: bool = False

    client, server = Host(), Host()
    up_signal, down_signal = [], []

    def update_up_signal():
        if server.highest_ts_val < packet.ts_val:
            up_signal.append(DataPoint(timestamp=packet.timestamp, spin_bit=client.spin_bit))
            server.highest_ts_val = packet.ts_val
            server.spin_bit = client.spin_bit

    def update_down_signal():
        if client.highest_ts_val < packet.ts_val:
            down_signal.append(DataPoint(timestamp=packet.timestamp, spin_bit=server.spin_bit))
            client.highest_ts_val = packet.ts_val
            client.spin_bit = not server.spin_bit

    for packet in packets_df.itertuples():
        if packet.ip_direction_asc:
            update_up_signal()
        else:
            update_down_signal()
    return up_signal, down_signal


def rtts_from_signal(flow_hash: str, signal: List[DataPoint]) -> pd.DataFrame:
    assert len(signal) > 0
    rtts: List[RTT] = []
    last_edge = signal[0]
    for datapoint in signal:
        if datapoint.spin_bit != last_edge.spin_bit:
            rtts.append(RTT(flow_hash=flow_hash,
                            timestamp=datapoint.timestamp,
                            rtt=datapoint.timestamp - last_edge.timestamp))
            last_edge = datapoint
    return pd.DataFrame(rtts, columns=RTT._fields)


def rtts_from_flow(flow: Tuple[str, pd.DataFrame]) -> pd.DataFrame:
    flow_hash, packets_df = flow
    signals = signals_from_flow(packets_df)
    return pd.concat(rtts_from_signal(flow_hash, signal) for signal in signals)
