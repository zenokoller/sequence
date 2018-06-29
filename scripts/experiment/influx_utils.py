import pandas as pd
from typing import Iterable, Set, List

from influxdb import DataFrameClient, InfluxDBClient
from influxdb.resultset import ResultSet

HTTP_SEQ_QUERY = 'select "losses", "packets" ' \
                 'from "telegraf"."autogen"."httpjson_knownsequence" ' \
                 'where time > {start_time} and time < {end_time};'

DOMAIN = 'client-domain-uplink'
HTTP_NETEM_QUERY = f'select "{DOMAIN}.packet.dropped" AS "losses",  ' \
                   f'"{DOMAIN}.packet.reordered" AS "reorders" ' \
                   f'from "telegraf"."autogen"."httpjson_netem" ' \
                   f'where time > {{start_time}} and time < {{end_time}};'

INFLUX_QUERY = 'select "offset" from "telegraf"."autogen"."{series}" ' \
               'where time > {start_time} and time < {end_time};'


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
        INFLUX_QUERY.format('loss', start_time, end_time)), 'receive', 'offset'))
