from dataclasses import dataclass
from pool.pool import Pool
from fee_algorithm.base import FeeAlgorithm
from user.abstract_user import User
from datetime import datetime
import pandas as pd
from simulation.simulation import SimulationResult


@dataclass
class ExperimentData:
    start_time: datetime
    end_time: datetime

    A_symbol: str = "ETH"
    B_symbol: str = "SHIB"
    stable_coin_symbol: str = "USDT"

    candle_interval: str = "5m"


@dataclass
class UninformedUsersConfig:
    uninformed_user: User
    probability_of_trade: float
    n_users: int


@dataclass
class Experiment:
    data: ExperimentData

    fee_algorithm: FeeAlgorithm

    informed_user: User
    uninformed_users: UninformedUsersConfig

    initial_pool_value: int = 26263564  # in stable coin

    network_fee: float = 5  # in stable coin


@dataclass
class ExperimentResult:
    data: pd.DataFrame
    experiment: Experiment
    pool: Pool
    simulation_result: SimulationResult
