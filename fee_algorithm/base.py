from dataclasses import dataclass
from abc import ABC, abstractmethod
from pool.liquidity_state import PoolLiquidityState, BalanceChange


@dataclass
class FeeAlgorithm(ABC):

    @abstractmethod
    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        pass

    @abstractmethod
    def get_b_to_a_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        pass

    @abstractmethod
    def process_trade(self, pool_balance_change: BalanceChange) -> None:
        pass

    @abstractmethod
    def process_oracle_price(self, a_to_b_price: float) -> None:
        pass

    @abstractmethod
    def inverse(self) -> "FeeAlgorithm":
        pass
