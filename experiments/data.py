from experiments.experiment import Experiment, ExperimentData
from pathlib import Path
from historical_data import get_historical_prices_for_two_assets
import logging
import pandas as pd


def get_cached_data_file_name(experiment_data: ExperimentData):
    return f"{experiment_data.start_time}_{experiment_data.end_time}_{experiment_data.A_symbol}_{experiment_data.B_symbol}_{experiment_data.stable_coin_symbol}_{experiment_data.candle_interval}.csv"


def download_data(path: Path, experiment_data: ExperimentData):
    df = get_historical_prices_for_two_assets(
        experiment_data.stable_coin_symbol,
        experiment_data.A_symbol,
        experiment_data.B_symbol,
        experiment_data.candle_interval,
        experiment_data.start_time,
        experiment_data.end_time,
    )
    df.to_csv(path, index=False)


def get_experiment_data(data_root: Path, experiment_data: ExperimentData):
    data_file_name = get_cached_data_file_name(experiment_data)
    data_file_path = data_root / data_file_name

    if not data_file_path.exists():
        logging.info(f"Cached data file {data_file_path} not found, downloading...")
        download_data(data_file_path, experiment_data)

    return pd.read_csv(data_file_path)
