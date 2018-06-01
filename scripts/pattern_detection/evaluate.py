import sys
from typing import Iterable, List

from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from pattern.gilbert_counts import GilbertCounts
from sequence.sequence import default_sequence_args


def evaluate(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Collects actual and predicted losses from InfluxDB after one experiment run and computes
    the paremeters for the Gilbert model."""

    # print(f'{start_time} {end_time}')

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
    actual_losses = (i for i in range(lower, upper) if not i in received)

    # compute parameters of Gilbert model
    detected_loss_params = compute_gilbert_params(detected_losses)
    actual_loss_params = compute_gilbert_params(actual_losses)

    print(f'\nGilbert Params\n--------------\nfrom detected losses: {detected_loss_params}\n'
          f'from actual losses: {actual_loss_params}')

    # symbol_bits = settings['client']['symbol_bits']
    # with open(csv_path, 'a+') as out_file:
    #     pass


def compute_gilbert_params(loss_offsets: Iterable[int]) -> dict:
    period = default_sequence_args['period']
    return GilbertCounts.from_loss_offsets(period, loss_offsets).to_params()


if __name__ == '__main__':
    try:
        start_time, end_time = sys.argv[1:3]
        csv_path = sys.argv[3]
    except IndexError:
        print('Usage: $0 <start_time> <end_time> <csv_path>')
    evaluate(start_time, end_time, csv_path, {})
