from functools import partial

from influxdb import DataFrameClient

from scripts.experiment.base_experiment import BaseExperiment, main


def latency_to_csv(start_time: int, end_time: int, csv_path: str, settings: dict):
    """Computes detection latencies for losses in number of packets after one experiment and
    stores it as csv."""
    client = DataFrameClient(database='telegraf')

    loss_df = client.query(
        f'select "offset", "found_offset" from "telegraf"."autogen"."loss" '
        f'where time > {start_time} and time < {end_time};')['loss']

    loss_df['packet_latency'] = loss_df['found_offset'] - loss_df['offset']

    batch_size = settings['server']['recovery_batch_size']
    with open(csv_path, 'a+') as out_file:
        out_file.writelines(f'{batch_size},{latency}\n'
                            for latency in loss_df.packet_latency)


PacketLatencyExperiment = partial(BaseExperiment,
                                  post_run_fn=latency_to_csv)

if __name__ == '__main__':
    main(PacketLatencyExperiment, config_file='config/packet_latency.yml')
