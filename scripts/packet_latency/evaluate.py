from influxdb import DataFrameClient


def evaluate(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Computes detection latencies for losses in number of packets after one experiment run."""
    client = DataFrameClient(database='telegraf')

    loss_df = client.query(
        f'select "offset", "found_offset" from "telegraf"."autogen"."loss" '
        f'where time > {start_time} and time < {end_time};')['loss']

    loss_df['packet_latency'] = loss_df['found_offset'] - loss_df['offset']

    symbol_bits = settings['client']['symbol_bits']
    with open(csv_path, 'a+') as out_file:
        out_file.writelines(f'{symbol_bits},{latency}\n' for latency in loss_df.packet_latency)
