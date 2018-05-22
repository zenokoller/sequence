from typing import Iterable

from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet


def evaluate(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Collects actual and predicted losses from InfluxDB after one experiment run."""
    client = InfluxDBClient(database='telegraf')
    query = f'select "offset" from "telegraf"."autogen"."{{series}}" ' \
            f'where time > {start_time} and time < {end_time};'

    def result_to_values(result: ResultSet, series: str, field: str) -> Iterable:
        return (item[field] for item in result.get_points(series))

    received = set(
        result_to_values(client.query(query.format(series='receive')), 'receive', 'offset'))
    detected_losses = set(
        result_to_values(client.query(query.format(series='loss')), 'loss', 'offset'))

    # derive actual loss offsets from received offsets
    lower, upper = min(received), max(received) + 1
    actual_losses = set([i for i in range(lower, upper) if not i in received])

    # compute precision and recall
    true_positive_count = len(actual_losses.intersection(detected_losses))
    positive_count = len(detected_losses)
    relevant_count = len(actual_losses)

    precision = true_positive_count / positive_count if positive_count > 0 else 0
    recall = true_positive_count / relevant_count if relevant_count > 0 else 0

    symbol_bits = settings['client']['symbol_bits']
    with open(csv_path, 'a+') as out_file:
        out_file.write(f'{symbol_bits},{precision},{recall}\n')
