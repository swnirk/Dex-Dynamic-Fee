from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class PoolLiquidityState:
    quantity_a: float
    quantity_b: float

    def inverse(self) -> "PoolLiquidityState":
        return PoolLiquidityState(self.quantity_b, self.quantity_a)

    # delta_a, delta_b are "user-side" quantities
    def process_trade(self, delta_a: float, delta_b: float):
        self.quantity_a -= delta_a
        self.quantity_b -= delta_b


@dataclass
class Pool(ABC):
    liquidity_state: PoolLiquidityState

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
    def process_trade(self, delta_a: float, delta_b: float):
        pass

    def get_a_to_b_exchange_price(self) -> float:
        return self.liquidity_state.quantity_b / self.liquidity_state.quantity_a
