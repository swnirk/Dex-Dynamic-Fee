from datetime import datetime

import numpy as np
import pandas as pd

from candle_interval import (
    get_binance_fetch_interval,
    normalize_candle_interval_for_binance,
    normalize_candle_interval_for_pandas,
)
from experiments.experiment import GBMParameters, SyntheticDataDescription
from experiments.synthetic_data import generate_synthetic_data
from historical_data import resample_klines


def test_interval_normalization_and_fetch_interval():
    assert normalize_candle_interval_for_pandas("12min") == "12min"
    assert normalize_candle_interval_for_pandas("12s") == "12s"
    assert normalize_candle_interval_for_binance("12min") == "12m"
    assert get_binance_fetch_interval("12min") == "3m"
    assert get_binance_fetch_interval("12s") == "1s"
    assert normalize_candle_interval_for_pandas("12m") == "12min"


def test_resample_klines_to_custom_interval():
    start = datetime(2024, 1, 1, 0, 0, 0)
    open_times = pd.date_range(start=start, periods=12, freq="1min")
    close_times = open_times + pd.Timedelta(minutes=1) - pd.Timedelta(milliseconds=1)

    source = pd.DataFrame(
        {
            "Open time": open_times,
            "Open": np.arange(1, 13, dtype=float),
            "High": np.arange(2, 14, dtype=float),
            "Low": np.arange(0, 12, dtype=float),
            "Close": np.arange(1.5, 13.5, dtype=float),
            "Volume": np.ones(12, dtype=float),
            "Close time": close_times,
            "Quote asset volume": np.ones(12, dtype=float) * 2,
            "Number of trades": np.ones(12, dtype=int),
            "Taker buy base asset volume": np.ones(12, dtype=float) * 3,
            "Taker buy quote asset volume": np.ones(12, dtype=float) * 4,
            "Ignore": np.zeros(12, dtype=int),
        }
    )

    resampled = resample_klines(source, target_interval="12min", origin=start)

    assert len(resampled) == 1
    assert resampled.loc[0, "Open time"] == pd.Timestamp(start)
    assert resampled.loc[0, "Open"] == 1.0
    assert resampled.loc[0, "High"] == 13.0
    assert resampled.loc[0, "Low"] == 0.0
    assert resampled.loc[0, "Close"] == 12.5
    assert resampled.loc[0, "Volume"] == 12.0
    assert resampled.loc[0, "Number of trades"] == 12
    assert resampled.loc[0, "Close time"] == close_times[-1]


def test_generate_synthetic_data_with_12_minute_frequency():
    description = SyntheticDataDescription(
        gbm_parameters=GBMParameters(
            S0=[100.0, 200.0],
            mu=[0.0, 0.0],
            cov_matrix=np.eye(2) * 0.01,
        ),
        start_time=datetime(2024, 1, 1, 0, 0, 0),
        end_time=datetime(2024, 1, 1, 1, 0, 0),
        candle_interval="12min",
    )

    data = generate_synthetic_data(description)

    assert len(data) == 6
    assert (data["time"].iloc[1] - data["time"].iloc[0]) == pd.Timedelta(minutes=12)
