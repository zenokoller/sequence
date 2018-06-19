from functools import partial

from influxdb import DataFrameClient

from scripts.experiment.base_experiment import BaseExperiment, main


def loss_rate_to_csv(start_time: int, end_time: int, csv_path: str, _: dict):
    """Collects loss events and netem stats from InfluxDB, computes loss rates and stores them
    as csv."""
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

    # bucketize data
    sequence_df = sequence_df.diff()

    diff_df = netem_df.diff()
    diff_df[diff_df < 0] = netem_df[diff_df < 0]  # netemd values are regularly reset
    netem_df = diff_df

    def compute_loss_rate(df, losses_name, packets_name):
        return (df[losses_name] / (df[losses_name] + df[packets_name])).fillna(0)

    joined_df = sequence_df.join(netem_df, lsuffix="_sequence", rsuffix="_netem")

    # Use netem packet counts to calculate sequence loss rate as shortcut to getting packet counts
    # from offsets in each interval
    joined_df['rate_sequence'] = compute_loss_rate(joined_df, 'losses_sequence', 'packets_netem')
    joined_df['rate_netem'] = compute_loss_rate(joined_df, 'losses_netem', 'packets_netem')

    joined_df.to_csv(csv_path)


RateExperiment = partial(BaseExperiment,
                         post_run_fn=loss_rate_to_csv)

if __name__ == '__main__':
    main(RateExperiment, config_file='config/rate_2_bit.yml')
