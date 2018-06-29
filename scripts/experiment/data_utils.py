def compute_rate(df, events_name, packets_name):
    return (df[events_name] / (df[events_name] + df[packets_name])).fillna(0)
