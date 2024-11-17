from dataclasses import dataclass
from pool.abstract_pool import Pool, PoolLiquidityState


@dataclass
class DynamicFeePool(Pool):
    liquidity_state: PoolLiquidityState

    alpha: float  # fee rate
    gamma: float

    def inverse_pool(self) -> "DynamicFeePool":
        return DynamicFeePool(self.liquidity_state.inverse(), self.alpha, self.gamma)

    def get_a_to_b_exchange_fee_rate(self) -> float:
        return self.alpha
    
    def get_b_to_a_exchange_fee_rate(self) -> float:
        return self.gamma

    def process_trade(self, delta_a: float, delta_b: float):
        self.liquidity_state.process_trade(delta_a, delta_b)
