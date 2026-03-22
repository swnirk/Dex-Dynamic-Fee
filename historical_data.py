from datetime import datetime
import requests
import pandas as pd

from candle_interval import (
    get_binance_fetch_interval,
    normalize_candle_interval_for_binance,
    normalize_candle_interval_for_pandas,
)

BINANCE_RESPONSE_COLUMNS = [
    "Open time",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Close time",
    "Quote asset volume",
    "Number of trades",
    "Taker buy base asset volume",
    "Taker buy quote asset volume",
    "Ignore",
]

BINANCE_API_URL = "https://api.binance.com/api/v3/klines"


def _convert_time_to_binance_format(time: datetime) -> int:
    return int((time.timestamp() * 1000))


def get_historical_data(
    symbol: str, interval: str, start_time: datetime, end_time: datetime
) -> pd.DataFrame:
    """
    Gets historical data from Binance API

    Args:
    symbol (str): The symbol to get data for
    interval (str): The interval for the data
    start_time (datetime): The start time for the data
    end_time (datetime): The end time for the data

    Returns:
    pd.DataFrame: The historical data
    """

    always_return_1 = False
    if symbol.upper() == "USDTUSDT":
        always_return_1 = True
        symbol = "ETHUSDT"

    fetch_interval = get_binance_fetch_interval(interval)
    requested_interval = normalize_candle_interval_for_binance(interval)

    params = {
        "symbol": symbol,
        "interval": fetch_interval,
        "startTime": _convert_time_to_binance_format(start_time),
        "endTime": _convert_time_to_binance_format(end_time),
        "limit": 1000,  # Binance API limit
    }
    data = []
    while True:
        response = requests.get(BINANCE_API_URL, params=params)
        temp_data = response.json()
        if not temp_data:
            break
        data.extend(temp_data)
        params["startTime"] = temp_data[-1][0] + 1

    data = pd.DataFrame(data, columns=BINANCE_RESPONSE_COLUMNS)
    data["Open time"] = pd.to_datetime(data["Open time"], unit="ms")
    data["Close time"] = pd.to_datetime(data["Close time"], unit="ms")

    for float_columns in [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Quote asset volume",
        "Taker buy base asset volume",
        "Taker buy quote asset volume",
    ]:
        data[float_columns] = data[float_columns].astype(float)

    data["Number of trades"] = data["Number of trades"].astype(int)

    if always_return_1:
        data["Open"] = 1
        data["High"] = 1
        data["Low"] = 1
        data["Close"] = 1

    if fetch_interval != requested_interval:
        data = resample_klines(
            data=data,
            target_interval=interval,
            origin=start_time,
        )

    return data


def resample_klines(
    data: pd.DataFrame, target_interval: str, origin: datetime
) -> pd.DataFrame:
    if data.empty:
        return data

    target_pandas_interval = normalize_candle_interval_for_pandas(target_interval)

    resampled = (
        data.set_index("Open time")
        .resample(target_pandas_interval, origin=origin, label="left", closed="left")
        .agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
                "Close time": "last",
                "Quote asset volume": "sum",
                "Number of trades": "sum",
                "Taker buy base asset volume": "sum",
                "Taker buy quote asset volume": "sum",
                "Ignore": "last",
            }
        )
        .dropna(subset=["Open"])
        .reset_index()
    )

    return resampled


def get_historical_prices_for_two_assets(
    stable_coin_symbol: str,
    A_symbol: str,
    B_symbol: str,
    interval: str,
    start_time: datetime,
    end_time: datetime,
):
    first_ticker = A_symbol + stable_coin_symbol
    second_ticker = B_symbol + stable_coin_symbol
    first_asset_data = get_historical_data(first_ticker, interval, start_time, end_time)
    second_asset_data = get_historical_data(
        second_ticker, interval, start_time, end_time
    )

    first_asset_data = first_asset_data[["Open time", "Close time", "Open"]]
    first_asset_data = first_asset_data.rename(columns={"Open": "price_A"})

    second_asset_data = second_asset_data[["Open time", "Close time", "Open"]]
    second_asset_data = second_asset_data.rename(columns={"Open": "price_B"})

    data = pd.merge(first_asset_data, second_asset_data, on=["Open time", "Close time"])
    data = data.drop(columns=["Close time"])
    data = data.rename(columns={"Open time": "time"})

    return data
