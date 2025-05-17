from datetime import datetime, timedelta
import requests
import pandas as pd

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

    params = {
        "symbol": symbol,
        "interval": interval,
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
    ]:
        data[float_columns] = data[float_columns].astype(float)

    if always_return_1:
        data["Open"] = 1
        data["High"] = 1
        data["Low"] = 1
        data["Close"] = 1

    return data


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
