import pandas as pd


def load_dataframe(path: str, key: str) -> pd.DataFrame:
    with pd.HDFStore(path) as store:
        return store[key]
