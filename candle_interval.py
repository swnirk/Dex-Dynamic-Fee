from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd


_INTERVAL_RE = re.compile(r"^(?P<value>\d+)\s*(?P<unit>[a-zA-Z]+)$")

# Preferred public notation in this repo is: s, min, h, d, w.
# Short aliases like "m" are still accepted for backward compatibility and
# normalized before use with pandas/Binance.

_PANDAS_UNIT_BY_ALIAS = {
    "s": "s",
    "sec": "s",
    "secs": "s",
    "second": "s",
    "seconds": "s",
    "m": "min",
    "min": "min",
    "mins": "min",
    "minute": "min",
    "minutes": "min",
    "h": "h",
    "hr": "h",
    "hrs": "h",
    "hour": "h",
    "hours": "h",
    "d": "D",
    "day": "D",
    "days": "D",
    "w": "W",
    "week": "W",
    "weeks": "W",
}

_BINANCE_UNIT_BY_PANDAS_UNIT = {
    "s": "s",
    "min": "m",
    "h": "h",
    "D": "d",
    "W": "w",
}

SUPPORTED_BINANCE_INTERVALS = {
    "1s",
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
}


@dataclass(frozen=True)
class ParsedCandleInterval:
    value: int
    pandas_unit: str

    def to_pandas_freq(self) -> str:
        return f"{self.value}{self.pandas_unit}"

    def to_binance_interval(self) -> str:
        unit = _BINANCE_UNIT_BY_PANDAS_UNIT.get(self.pandas_unit)
        if unit is None:
            raise ValueError(f"Unsupported Binance interval unit: {self.pandas_unit}")
        return f"{self.value}{unit}"

    def to_timedelta(self) -> pd.Timedelta:
        return pd.to_timedelta(self.to_pandas_freq())


def parse_candle_interval(interval: str) -> ParsedCandleInterval:
    match = _INTERVAL_RE.fullmatch(interval.strip())
    if match is None:
        raise ValueError(f"Unsupported candle interval format: {interval}")

    value = int(match.group("value"))
    raw_unit = match.group("unit").lower()
    pandas_unit = _PANDAS_UNIT_BY_ALIAS.get(raw_unit)
    if pandas_unit is None:
        raise ValueError(f"Unsupported candle interval unit: {interval}")

    if value <= 0:
        raise ValueError(f"Candle interval must be positive: {interval}")

    return ParsedCandleInterval(value=value, pandas_unit=pandas_unit)


def normalize_candle_interval_for_pandas(interval: str) -> str:
    return parse_candle_interval(interval).to_pandas_freq()


def normalize_candle_interval_for_binance(interval: str) -> str:
    return parse_candle_interval(interval).to_binance_interval()


def get_binance_fetch_interval(interval: str) -> str:
    requested = normalize_candle_interval_for_binance(interval)
    if requested in SUPPORTED_BINANCE_INTERVALS:
        return requested

    requested_td = parse_candle_interval(interval).to_timedelta()

    supported_by_size = sorted(
        (
            (pd.to_timedelta(normalize_candle_interval_for_pandas(candidate)), candidate)
            for candidate in SUPPORTED_BINANCE_INTERVALS
        ),
        reverse=True,
    )

    for candidate_td, candidate in supported_by_size:
        if candidate_td <= requested_td and requested_td % candidate_td == pd.Timedelta(0):
            return candidate

    raise ValueError(
        f"Unsupported candle interval for Binance fetch/resample pipeline: {interval}"
    )
