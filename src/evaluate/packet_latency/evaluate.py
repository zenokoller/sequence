#!/usr/bin/env python

"""Computes detection latencies for losses in number of packets after one experiment run."""
import sys

from influxdb import DataFrameClient

try:
    start_time, end_time = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3]
    symbol_bits = sys.argv[4]
except IndexError:
    print('Usage: $0 <start_time> <end_time> <out_path> <symbol_bits>')
    sys.exit(0)

client = DataFrameClient(database='telegraf')

loss_df = client.query(
    f'select "offset", "found_offset" from "telegraf"."autogen"."loss" '
    f'where time > {start_time} and time < {end_time};')['loss']

loss_df['packet_latency'] = loss_df['found_offset'] - loss_df['offset']

with open(out_path, 'a+') as out_file:
    out_file.writelines(f'{symbol_bits},{latency}\n' for latency in loss_df.packet_latency)
