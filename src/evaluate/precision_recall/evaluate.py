#!/usr/bin/env python

import sys
from typing import Iterable

from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

"""Collects actual and predicted losses from InfluxDB after one experiment run."""

try:
    start_time, end_time = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3]
    symbol_bits = sys.argv[4]
except IndexError:
    print('Usage: $0 <start_time> <end_time> <out_path> <symbol_bits>')
    sys.exit(0)

# read received offsets and detected loss offsets from InfluxDB
client = InfluxDBClient(database='telegraf')

query = f'select "offset" from "telegraf"."autogen"."{{series}}" ' \
        f'where time > {start_time} and time < {end_time};'


def result_to_values(result: ResultSet, series: str, field: str) -> Iterable:
    return (item[field] for item in result.get_points(series))


received = set(result_to_values(client.query(query.format(series='receive')), 'receive', 'offset'))
detected_losses = set(result_to_values(client.query(query.format(series='loss')), 'loss', 'offset'))

# derive actual loss offsets from received offsets
lower, upper = min(received), max(received) + 1
actual_losses = set([i for i in range(lower, upper) if not i in received])

# compute precision and recall
true_positive_count = len(actual_losses.intersection(detected_losses))
precision = true_positive_count / len(detected_losses)
recall = true_positive_count / len(actual_losses)

with open(out_path, 'a+') as out_file:
    out_file.write(f'{symbol_bits},{precision},{recall}\n')
