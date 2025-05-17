from dataclasses import dataclass
from pool.pool import Pool
from fee_algorithm.base import FeeAlgorithm
from user.abstract_user import User
from datetime import datetime
import pandas as pd
from simulation.simulation import SimulationResult
import numpy as np
from typing import Union


@dataclass
class HistoricalDataDescription:
    start_time: datetime
    end_time: datetime

    A_symbol: str = "ETH"
    B_symbol: str = "SHIB"
    stable_coin_symbol: str = "USDT"

    candle_interval: str = "1m"

    cache_data: bool = True


@dataclass
class GBMParameters:
    """
    A dataclass to store parameters of a Geometric Brownian Motion (GBM).
    """

    S0: list[float]  # Initial prices
    mu: list[float]  # Drift (mean return)
    cov_matrix: np.ndarray  # Covariance matrix of log returns


@dataclass
class SyntheticDataDescription:
    gbm_parameters: GBMParameters

    start_time: datetime
    end_time: datetime
    candle_interval: str = (
        "1min"  # Slightly different notation because of Binance API peculiarities
    )


InputDataDescription = Union[HistoricalDataDescription, SyntheticDataDescription]


@dataclass
class UninformedUsersConfig:
    uninformed_user: User
    probability_of_trade: float
    n_users: int


@dataclass
class Experiment:
    data: InputDataDescription

    fee_algorithm: FeeAlgorithm

    informed_user: User
    uninformed_users: UninformedUsersConfig

    initial_pool_value: int = 25 * 1000000  # in stable coin

    network_fee: float = 5  # in stable coin

    random_seed: int = 0


@dataclass
class ExperimentResult:
    data: pd.DataFrame
    experiment: Experiment
    pool: Pool
    simulation_result: SimulationResult
