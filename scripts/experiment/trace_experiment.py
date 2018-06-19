from functools import partial
from typing import Iterable

import pandas as pd
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from scripts.experiment.base_experiment import BaseExperiment, main


def event_trace_to_csv(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Collects the loss events from InfluxDB and stores them as csv."""
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
    try:
        lower, upper = min(received), max(received) + 1
    except:
        print('Found no received offsets!')
        return

    loss_df = pd.DataFrame({
        'actual': [0 if i in received else 1 for i in range(lower, upper)],
        'detected': [1 if i in detected_losses else 0 for i in range(lower, upper)]})

    loss_df.to_csv(csv_path, mode='a+')


TraceExperiment = partial(BaseExperiment,
                          post_run_fn=event_trace_to_csv)

if __name__ == '__main__':
    main(TraceExperiment, config_file='config/trace_2_bit.yml')
