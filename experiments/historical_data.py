from experiments.experiment import HistoricalDataDescription
from pathlib import Path
from historical_data import get_historical_prices_for_two_assets
import logging
import pandas as pd


def get_cached_historical_data_file_name(description: HistoricalDataDescription):
    return f"{description.start_time}_{description.end_time}_{description.A_symbol}_{description.B_symbol}_{description.stable_coin_symbol}_{description.candle_interval}.csv"


def download_historical_data(path: Path, description: HistoricalDataDescription):
    df = get_historical_prices_for_two_assets(
        description.stable_coin_symbol,
        description.A_symbol,
        description.B_symbol,
        description.candle_interval,
        description.start_time,
        description.end_time,
    )
    df.to_csv(path, index=False)


def get_experiment_historical_data(
    data_root: Path, description: HistoricalDataDescription
):
    if description.cache_data:
        data_file_name = get_cached_historical_data_file_name(description)
        data_file_path = data_root / data_file_name

        if not data_file_path.exists():
            logging.info(f"Cached data file {data_file_path} not found, downloading...")
            download_historical_data(data_file_path, description)

        return pd.read_csv(data_file_path)
    else:
        return get_historical_prices_for_two_assets(
            description.stable_coin_symbol,
            description.A_symbol,
            description.B_symbol,
            description.candle_interval,
            description.start_time,
            description.end_time,
        )
