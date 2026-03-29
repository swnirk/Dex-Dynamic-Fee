"""
Download 1s klines from Binance Vision and save to the data cache.

Usage:
    python download_binance_vision.py \
        --start "2024-03-15 12:00:00" \
        --end   "2024-03-16 12:00:00" \
        --a-symbol ETH \
        --b-symbol SHIB \
        --stable USDT \
        --interval 12s \
        --data-dir visualizations/data

Binance Vision provides 1s klines in daily zip files:
    https://data.binance.vision/data/spot/daily/klines/{SYMBOL}/1s/{SYMBOL}-1s-{YYYY}-{MM}-{DD}.zip
"""

import argparse
import io
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

BINANCE_VISION_BASE = "https://data.binance.vision/data/spot/daily/klines"
BINANCE_VISION_MONTHLY = "https://data.binance.vision/data/spot/monthly/klines"

KLINES_COLUMNS = [
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

PANDAS_FREQ_MAP = {
    "s": "s",
    "min": "min",
    "m": "min",
    "h": "h",
    "d": "D",
}


def _parse_interval(interval: str) -> str:
    """Convert e.g. '12s', '1min' -> pandas resample freq string."""
    import re

    m = re.fullmatch(r"(\d+)\s*([a-zA-Z]+)", interval.strip())
    if not m:
        raise ValueError(f"Cannot parse interval: {interval}")
    value, unit = m.group(1), m.group(2).lower()
    pandas_unit = PANDAS_FREQ_MAP.get(unit)
    if pandas_unit is None:
        raise ValueError(f"Unknown interval unit: {unit}")
    return f"{value}{pandas_unit}"


def download_monthly_zips(
    symbols: list[str],
    start: datetime,
    end: datetime,
    interval: str,
    out_dir: Path,
) -> list[Path]:
    """Download monthly klines zip files from Binance Vision. No extraction."""
    out_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []

    year, month = start.year, start.month
    end_year, end_month = end.year, end.month

    while (year, month) <= (end_year, end_month):
        for symbol in symbols:
            filename = f"{symbol}-{interval}-{year:04d}-{month:02d}.zip"
            out_path = out_dir / filename
            if out_path.exists():
                print(f"  Already exists: {filename}")
                downloaded.append(out_path)
            else:
                url = f"{BINANCE_VISION_MONTHLY}/{symbol}/{interval}/{filename}"
                print(f"  GET {url}", flush=True)
                resp = requests.get(url, timeout=600, stream=True)
                resp.raise_for_status()
                total = int(resp.headers.get("content-length", 0))
                chunks = []
                with tqdm(total=total, unit="B", unit_scale=True, desc=filename) as bar:
                    for chunk in resp.iter_content(chunk_size=1024 * 256):
                        chunks.append(chunk)
                        bar.update(len(chunk))
                out_path.write_bytes(b"".join(chunks))
                downloaded.append(out_path)

        month += 1
        if month > 12:
            month, year = 1, year + 1

    return downloaded


def _download_day(symbol: str, date: datetime) -> pd.DataFrame:
    """Download 1s klines for one day from Binance Vision."""
    date_str = date.strftime("%Y-%m-%d")
    url = f"{BINANCE_VISION_BASE}/{symbol}/1s/{symbol}-1s-{date_str}.zip"

    print(f"  Downloading {url} ...", flush=True)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        csv_name = zf.namelist()[0]
        with zf.open(csv_name) as f:
            df = pd.read_csv(f, header=None, names=KLINES_COLUMNS)

    df["Open time"] = pd.to_datetime(df["Open time"], unit="ms", utc=True)
    df["Open time"] = df["Open time"].dt.tz_convert(None)  # remove tz
    df["Open"] = df["Open"].astype(float)
    return df[["Open time", "Open"]]


def _download_symbol(
    symbol: str,
    start: datetime,
    end: datetime,
) -> pd.DataFrame:
    """Download and concatenate all necessary days for symbol."""
    # Iterate over calendar days that overlap [start, end]
    day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = end.replace(hour=0, minute=0, second=0, microsecond=0)

    frames = []
    while day <= end_day:
        try:
            frames.append(_download_day(symbol, day))
        except requests.HTTPError as e:
            print(f"  WARNING: {e} — skipping {day.date()}")
        day += timedelta(days=1)

    if not frames:
        raise RuntimeError(f"No data downloaded for {symbol}")

    df = pd.concat(frames, ignore_index=True)
    df = df[(df["Open time"] >= start) & (df["Open time"] <= end)]
    df = df.sort_values("Open time").reset_index(drop=True)
    return df


def _resample(df: pd.DataFrame, interval: str, start: datetime) -> pd.DataFrame:
    freq = _parse_interval(interval)
    resampled = (
        df.set_index("Open time")
        .resample(freq, origin=start, label="left", closed="left")["Open"]
        .first()
        .dropna()
        .reset_index()
    )
    return resampled


def _cache_filename(
    start: datetime,
    end: datetime,
    a_symbol: str,
    b_symbol: str,
    stable: str,
    interval: str,
) -> str:
    return f"{start}_{end}_{a_symbol}_{b_symbol}_{stable}_{interval}.csv"


def download_and_cache(
    start: datetime,
    end: datetime,
    a_symbol: str,
    b_symbol: str,
    stable: str,
    interval: str,
    data_dir: Path,
) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)

    out_path = data_dir / _cache_filename(
        start, end, a_symbol, b_symbol, stable, interval
    )
    if out_path.exists():
        print(f"Already cached: {out_path}")
        return out_path

    ticker_a = a_symbol + stable if a_symbol.upper() != stable.upper() else None
    ticker_b = b_symbol + stable if b_symbol.upper() != stable.upper() else None

    print(f"Downloading {ticker_a} ...")
    if ticker_a:
        df_a = _download_symbol(ticker_a, start, end)
        df_a = _resample(df_a, interval, start)
        df_a = df_a.rename(columns={"Open": "price_A"})
    else:
        # stable/stable — price is always 1
        df_a = pd.DataFrame(
            {
                "Open time": pd.date_range(start, end, freq=_parse_interval(interval)),
                "price_A": 1.0,
            }
        )

    print(f"Downloading {ticker_b} ...")
    if ticker_b:
        df_b = _download_symbol(ticker_b, start, end)
        df_b = _resample(df_b, interval, start)
        df_b = df_b.rename(columns={"Open": "price_B"})
    else:
        df_b = pd.DataFrame({"Open time": df_a["Open time"], "price_B": 1.0})

    merged = pd.merge(df_a, df_b, on="Open time")
    merged = merged.rename(columns={"Open time": "time"})

    merged.to_csv(out_path, index=False)
    print(f"Saved {len(merged)} rows → {out_path}")
    return out_path


def resample_pair(
    symbol_a: str,
    symbol_b: str,
    zip_dir: Path,
    out_dir: Path,
    interval: str,
) -> None:
    """Resample already-downloaded zip files for a pair to time,price_A,price_B CSVs."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # Find all months available for symbol_a
    zips_a = sorted(zip_dir.glob(f"{symbol_a}-1s-*.zip"))
    if not zips_a:
        raise FileNotFoundError(f"No zips found for {symbol_a} in {zip_dir}")

    for zip_a in zips_a:
        # e.g. ETHUSDT-1s-2024-03.zip → SHIBUSDT-1s-2024-03.zip
        month_suffix = zip_a.name[len(symbol_a):]  # "-1s-2024-03.zip"
        zip_b = zip_dir / f"{symbol_b}{month_suffix}"
        if not zip_b.exists():
            print(f"  Skipping {zip_a.name}: no matching {zip_b.name}")
            continue

        out_name = f"{zip_a.stem.replace('-1s-', f'-{interval}-').replace(symbol_a, f'{symbol_a}_{symbol_b}')}.csv"
        out_path = out_dir / out_name
        if out_path.exists():
            print(f"  Already exists: {out_name}")
            continue

        print(f"  Resampling {zip_a.name} + {zip_b.name} → {out_name} ...", flush=True)

        def read_zip(path: Path) -> pd.DataFrame:
            with zipfile.ZipFile(path) as zf:
                with zf.open(zf.namelist()[0]) as f:
                    df = pd.read_csv(f, header=None, names=KLINES_COLUMNS)
            df["Open time"] = pd.to_datetime(df["Open time"], unit="ms", utc=True).dt.tz_convert(None)
            df["Open"] = df["Open"].astype(float)
            return df[["Open time", "Open"]]

        df_a = read_zip(zip_a)
        df_b = read_zip(zip_b)

        origin = df_a["Open time"].iloc[0]
        freq = _parse_interval(interval)

        def do_resample(df: pd.DataFrame) -> pd.DataFrame:
            return (
                df.set_index("Open time")
                .resample(freq, origin=origin, label="left", closed="left")["Open"]
                .first()
                .dropna()
                .reset_index()
            )

        df_a = do_resample(df_a).rename(columns={"Open": "price_A", "Open time": "time"})
        df_b = do_resample(df_b).rename(columns={"Open": "price_B", "Open time": "time"})

        merged = pd.merge(df_a, df_b, on="time")
        merged.to_csv(out_path, index=False)
        print(f"  Saved {len(merged)} rows → {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Download Binance Vision klines")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- download-zips: just fetch monthly zip files ---
    p_zips = subparsers.add_parser("download-zips", help="Download monthly zip files")
    p_zips.add_argument("--symbols", required=True, nargs="+",
                        help="Binance symbols, e.g. ETHUSDT SHIBUSDT")
    p_zips.add_argument("--start", required=True, help="e.g. '2024-03-01'")
    p_zips.add_argument("--end",   required=True, help="e.g. '2024-04-30'")
    p_zips.add_argument("--interval", default="1s")
    p_zips.add_argument("--out-dir", default="visualizations/data/zips")

    # --- resample: extract zips + resample + merge pair into CSV ---
    p_res = subparsers.add_parser("resample", help="Resample downloaded zips into time,price_A,price_B CSVs")
    p_res.add_argument("--symbol-a", required=True, help="e.g. ETHUSDT")
    p_res.add_argument("--symbol-b", required=True, help="e.g. SHIBUSDT")
    p_res.add_argument("--zip-dir",  default="visualizations/data/zips")
    p_res.add_argument("--out-dir",  default="visualizations/data/new_data")
    p_res.add_argument("--interval", default="12s")

    # --- cache: full pipeline (download 1s + resample + merge) ---
    p_cache = subparsers.add_parser("cache", help="Download, resample and save cache CSV")
    p_cache.add_argument("--start", required=True)
    p_cache.add_argument("--end",   required=True)
    p_cache.add_argument("--a-symbol", default="ETH")
    p_cache.add_argument("--b-symbol", default="SHIB")
    p_cache.add_argument("--stable",   default="USDT")
    p_cache.add_argument("--interval", default="12s")
    p_cache.add_argument("--data-dir", default="visualizations/data")

    args = parser.parse_args()
    fmt_long  = "%Y-%m-%d %H:%M:%S"
    fmt_short = "%Y-%m-%d"

    def _parse_dt(s):
        for fmt in (fmt_long, fmt_short):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                pass
        raise ValueError(f"Cannot parse date: {s}")

    if args.command == "download-zips":
        download_monthly_zips(
            symbols=args.symbols,
            start=_parse_dt(args.start),
            end=_parse_dt(args.end),
            interval=args.interval,
            out_dir=Path(args.out_dir),
        )
    elif args.command == "resample":
        resample_pair(
            symbol_a=args.symbol_a,
            symbol_b=args.symbol_b,
            zip_dir=Path(args.zip_dir),
            out_dir=Path(args.out_dir),
            interval=args.interval,
        )
    elif args.command == "cache":
        download_and_cache(
            start=_parse_dt(args.start),
            end=_parse_dt(args.end),
            a_symbol=args.a_symbol,
            b_symbol=args.b_symbol,
            stable=args.stable,
            interval=args.interval,
            data_dir=Path(args.data_dir),
        )


if __name__ == "__main__":
    main()
