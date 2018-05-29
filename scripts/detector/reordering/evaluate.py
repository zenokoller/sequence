from influxdb import DataFrameClient


def evaluate(start_time: int, end_time: int, csv_path: str, _: dict):
    """Computes reordering rate as of RFC4737 for each interval and writes to file, along with
    actual reordering rate."""
    client = DataFrameClient(database='telegraf')

    sequence_df = client.query(
        f'select "delays", "packets" '
        f'from "telegraf"."autogen"."httpjson_knownsequence" '
        f'where time > {start_time} and time < {end_time};')['httpjson_knownsequence']

    domain = "client-domain-uplink"
    netem_df = client.query(
        f'select "{domain}.packet.reordered" AS "reorders", "{domain}.packet.count" AS "packets" '
        f'from "telegraf"."autogen"."httpjson_netem" '
        f'where time > {start_time} and time < {end_time};')['httpjson_netem']

    # bucketize data
    sequence_df = sequence_df.diff()

    diff_df = netem_df.diff()
    diff_df[diff_df < 0] = netem_df[diff_df < 0]  # netemd values are regularly reset
    netem_df = diff_df

    def compute_reordering_rate(df, reorders_name, packets_name):
        return (df[reorders_name] / (df[reorders_name] + df[packets_name])).fillna(0)

    joined_df = sequence_df.join(netem_df, lsuffix="_sequence", rsuffix="_netem")

    # Use netem packet counts to calculate sequence reordering rate as shortcut to getting packet
    # counts from offsets in each bucket
    joined_df['rate_sequence'] = compute_reordering_rate(joined_df, 'reorders_sequence',
                                                         'packets_netem')
    joined_df['rate_netem'] = compute_reordering_rate(joined_df, 'reorders_netem', 'packets_netem')

    joined_df.to_csv(csv_path)
