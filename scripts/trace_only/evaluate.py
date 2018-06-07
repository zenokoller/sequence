import sys
from typing import Iterable

import pandas as pd
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet


def evaluate(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Collects actual and predicted losses from InfluxDB after one experiment run and computes
    the paremeters for the Gilbert model."""

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

    loss_df = pd.DataFrame({
        'actual': [0 if i in received else 1 for i in range(lower, upper)],
        'detected': [1 if i in detected_losses else 0 for i in range(lower, upper)]})

    loss_df.to_csv(csv_path, mode='a+')


if __name__ == '__main__':
    try:
        start_time, end_time = sys.argv[1:3]
        csv_path = sys.argv[3]
    except IndexError:
        print('Usage: $0 <start_time> <end_time> <csv_path>')
    evaluate(start_time, end_time, csv_path)
