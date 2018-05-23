from influxdb import DataFrameClient


def evaluate(start_time: int, end_time: int, csv_path: str, _: dict):
    """Computes the packet rate for each second and writes to file, along with actual packet loss
    rate."""
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

    # compute loss rates
    joined_df = sequence_df.join(netem_df, lsuffix="_sequence", rsuffix="_netem")
    joined_df['rate_sequence'] = (
            joined_df['losses_sequence'] / joined_df['packets_netem']  # shortcut to get packet rate
    ).fillna(0)
    joined_df['rate_netem'] = (joined_df['losses_netem'] / joined_df['packets_netem']).fillna(0)

    joined_df.to_csv(csv_path)
