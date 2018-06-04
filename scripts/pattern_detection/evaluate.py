import sys
from typing import Iterable, List

import pandas as pd
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from pattern.gilbert_counts import GilbertCounts
from sequence.sequence import default_sequence_args


def evaluate(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Collects actual and predicted losses from InfluxDB after one experiment run and computes
    the paremeters for the Gilbert model."""

    print(f'\n{start_time} {end_time}')

    client = InfluxDBClient(database='telegraf')
    query = f'select "offset" from "telegraf"."autogen"."{{series}}" ' \
            f'where time > {start_time} and time < {end_time};'

    def result_to_values(result: ResultSet, series: str, field: str) -> Iterable:
        return (item[field] for item in result.get_points(series))

    received = list(
        result_to_values(client.query(query.format(series='receive')), 'receive', 'offset'))
    detected_losses = list(
        result_to_values(client.query(query.format(series='loss')), 'loss', 'offset'))

    # derive actual loss offsets from received offsets
    lower, upper = min(received), max(received) + 1
    actual_losses = list(i for i in range(lower, upper) if not i in received)

    params_df = pd.concat([gilbert_params_by_trace_lengths(detected_losses, 'sequence'),
                           gilbert_params_by_trace_lengths(actual_losses, 'ground_truth')])

    params_df['symbol_bits'] = settings['client']['symbol_bits']
    params_df.to_csv(csv_path)


def gilbert_params_by_trace_lengths(loss_offsets: List[int], source: str) -> pd.DataFrame:
    max_packets = max(loss_offsets)
    powers_of_ten = (10 ** k for k in range(2, 5))
    dataframes = [
        pd.DataFrame({'trace_length': trace_length, 'source': source,
                      **compute_gilbert_params(loss_offsets[:trace_length])},
                     index=[i]) for i, trace_length in enumerate(powers_of_ten)]
    return pd.concat(dataframes)


def compute_gilbert_params(loss_offsets: Iterable[int]) -> dict:
    period = default_sequence_args['period']
    return GilbertCounts.from_loss_offsets(period, loss_offsets).to_params()


if __name__ == '__main__':
    try:
        start_time, end_time = sys.argv[1:3]
        csv_path = sys.argv[3]
    except IndexError:
        print('Usage: $0 <start_time> <end_time> <csv_path>')
    evaluate(start_time, end_time, csv_path)
