from dataclasses import dataclass
from pool.abstract_pool import Pool, PoolLiquidityState


@dataclass
class SimplePool(Pool):
    liquidity_state: PoolLiquidityState

    alpha: float  # fee rate

    def inverse_pool(self) -> "SimplePool":
        return SimplePool(self.liquidity_state.inverse(), self.alpha)

    def get_a_to_b_exchange_fee_rate(self) -> float:
        return self.alpha

    def get_b_to_a_exchange_fee_rate(self) -> float:
        return self.alpha

    def get_b_to_a_exchange_fee_rate(self) -> float:
        return self.alpha

    def process_trade(self, delta_a: float, delta_b: float):
        self.liquidity_state.process_trade(delta_a, delta_b)
