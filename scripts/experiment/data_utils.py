def compute_loss_rate(df, losses_name, packets_name):
    return (df[losses_name] / (df[losses_name] + df[packets_name])).fillna(0)


def compute_reordering_rate(df, reorders_name, packets_name):
    return (df[reorders_name] / df[packets_name]).fillna(0)
