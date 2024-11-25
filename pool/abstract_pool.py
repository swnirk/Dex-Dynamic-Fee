from dataclasses import dataclass
from abc import ABC, abstractmethod
from balance_change import BalanceChange


@dataclass
class PoolLiquidityState:
    quantity_a: float
    quantity_b: float

    def inverse(self) -> "PoolLiquidityState":
        return PoolLiquidityState(self.quantity_b, self.quantity_a)

    def process_trade(self, balance_change: BalanceChange):
        self.quantity_a += balance_change.delta_x
        self.quantity_b += balance_change.delta_y


@dataclass
class Pool(ABC):
    liquidity_state: PoolLiquidityState
    AMM_algo: # smth
    Fee_algo: # smth

    @abstractmethod
    def inverse_pool(self) -> "Pool":
        pass

    @abstractmethod
    def get_a_to_b_exchange_fee_rate(self) -> float:
        pass

    @abstractmethod
    def get_b_to_a_exchange_fee_rate(self) -> float:
        pass

    @abstractmethod
    def process_trade(self, balance_change: BalanceChange):
        pass

    def get_a_to_b_exchange_price(self) -> float:
        return self.liquidity_state.quantity_b / self.liquidity_state.quantity_a
