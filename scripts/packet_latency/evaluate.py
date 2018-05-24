from influxdb import DataFrameClient


def evaluate(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Computes detection latencies for losses in number of packets after one experiment run."""
    client = DataFrameClient(database='telegraf')

    loss_df = client.query(
        f'select "offset", "found_offset" from "telegraf"."autogen"."loss" '
        f'where time > {start_time} and time < {end_time};')['loss']

    loss_df['packet_latency'] = loss_df['found_offset'] - loss_df['offset']

    batch_size = settings['server']['recovery_batch_size']
    min_match_size = settings['server']['recovery_min_match_size']
    range_length = settings['server']['recovery_range_length']

    with open(csv_path, 'a+') as out_file:
        out_file.writelines(f'{batch_size},{min_match_size},{range_length},{latency}\n'
                            for latency in loss_df.packet_latency)
