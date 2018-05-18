#!/usr/bin/env python

import sys

from influxdb import DataFrameClient

"""Computes the packet rate for each second and writes to file, along with actual packet loss 
rate."""

try:
    start_time, end_time = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3]
except IndexError:
    print('Usage: $0 <start_time> <end_time> <out_path>')
    sys.exit(0)

client = DataFrameClient(database='telegraf')

sequence_df = client.query(
    f'select "losses", "packets" '
    f'from "telegraf"."autogen"."httpjson_knownsequence" '
    f'where time > {start_time} and time < {end_time};')['httpjson_knownsequence']

domain = "client-domain-uplink"
netem_df = client.query(
    f'select "{domain}.packet.dropped" AS "losses", "{domain}.packet.count" AS "packets" '
    f'from "telegraf"."autogen"."httpjson_netem" '
    f'where time > {start_time} and time < {end_time};')['httpjson_netem']

# bucketize data and compute loss rates
sequence_df = sequence_df.diff()
sequence_df['rate'] = (sequence_df['losses'] / sequence_df['packets']).fillna(0)
sequence_df = sequence_df.filter(items=['rate'])

diff_df = netem_df.diff()
diff_df[diff_df < 0] = netem_df[diff_df < 0]  # netemd values are temporarily reset
netem_df = diff_df
netem_df['rate'] = (netem_df['losses'] / netem_df['packets']).fillna(0)
netem_df = netem_df.filter(items=['rate'])

joined_df = sequence_df.join(netem_df, lsuffix="_sequence", rsuffix="_netem")
joined_df.to_csv(out_path)