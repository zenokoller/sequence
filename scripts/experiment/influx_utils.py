from typing import Iterable, Set, Dict, List

import pandas as pd
from influxdb import DataFrameClient, InfluxDBClient
from influxdb.resultset import ResultSet

HTTP_SEQ_QUERY = 'select "losses", "packets", "reorders" ' \
                 'from "telegraf"."autogen"."httpjson_knownsequence" ' \
                 'where time > {0} and time < {1};'

DOMAIN = 'client-domain-uplink'
HTTP_NETEM_QUERY = f'select "{DOMAIN}.packet.dropped" AS "losses",  ' \
                   f'"{DOMAIN}.packet.reordered" AS "reorders" ' \
                   f'from "telegraf"."autogen"."httpjson_netem" ' \
                   f'where time > {{0}} and time < {{1}};'

INFLUX_QUERY = 'select "offset" from "telegraf"."autogen"."{0}" ' \
               'where time > {1} and time < {2};'

INFLUX_REORDER_QUERY = 'select "offset", "amount" from "telegraf"."autogen"."reordering" ' \
               'where time > {0} and time < {1};'


def get_sequence_df(client: DataFrameClient, start_time: int, end_time: int) -> pd.DataFrame:
    try:
        df = client.query(HTTP_SEQ_QUERY.format(start_time, end_time))['httpjson_knownsequence']
    except IndexError:
        raise Exception('Could not find any known sequence values in InfluxDB!')

    # bucketize data
    return df.diff()


def get_netem_df(client: DataFrameClient, start_time: int, end_time: int) -> pd.DataFrame:
    try:
        df = client.query(HTTP_NETEM_QUERY.format(start_time, end_time))['httpjson_netem']
    except IndexError:
        raise Exception('Could not find any netem values in InfluxDB!')

    # bucketize data
    diff_df = df.diff()
    diff_df[diff_df < 0] = df[diff_df < 0]  # netemd values are regularly reset
    return diff_df


def get_actual_losses(client: InfluxDBClient, start_time: int, end_time: int) -> Set[int]:
    received = set(result_to_values(client.query(
        INFLUX_QUERY.format('receive', start_time, end_time)), 'receive', 'offset'))

    try:  # derive actual loss offsets from received offsets
        lower, upper = min(received), max(received) + 1
    except ValueError:
        raise Exception('No received values have been found. Did the server crash?')

    return set([i for i in range(lower, upper) if not i in received])


def result_to_values(result: ResultSet, series: str, field: str) -> Iterable:
    return (item[field] for item in result.get_points(series))


def get_detected_losses(client: InfluxDBClient, start_time: int, end_time: int) -> Set[int]:
    return set(result_to_values(client.query(
        INFLUX_QUERY.format('loss', start_time, end_time)), 'loss', 'offset'))


def get_actual_reorders(client: InfluxDBClient, start_time: int, end_time: int) \
        -> Dict[int, int]:
    received = list(result_to_values(client.query(
        INFLUX_QUERY.format('receive', start_time, end_time)), 'receive', 'offset'))
    return reordering_extents(received)


def reordering_extents(seq_nrs: List[int]) -> Dict[int, int]:
    extents = {}
    next = seq_nrs[0] + 1
    missing = {}
    for i, seq_nr in enumerate(seq_nrs[1:]):
        if next < seq_nr:
            for j in range(next, seq_nr):
                missing[j] = i
            next = seq_nr + 1
        else:
            if seq_nr in missing:
                extents[seq_nr] = i - missing[seq_nr]
                del missing[seq_nr]
            else:
                next = seq_nr + 1

    return extents


def get_detected_reorders(client: InfluxDBClient, start_time: int, end_time: int) \
        -> Dict[int, int]:
    reorders_result = client.query(
        INFLUX_REORDER_QUERY.format(start_time, end_time))

    return {offset: amount for offset, amount in zip(
        result_to_values(reorders_result, 'reordering', 'offset'),
        result_to_values(reorders_result, 'reordering', 'amount'))}
