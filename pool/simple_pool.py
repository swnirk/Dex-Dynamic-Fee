from dataclasses import dataclass
from pool.abstract_pool import Pool, PoolLiquidityState
from balance_change import BalanceChange


@dataclass
class SimplePool(Pool):
    liquidity_state: PoolLiquidityState
    AMM_algo: str

    alpha: float  # fee rate

    def inverse_pool(self) -> "SimplePool":
        return SimplePool(self.liquidity_state.inverse(), self.AMM_algo, self.alpha)

    def get_a_to_b_exchange_fee_rate(self) -> float:
        return self.alpha

    def get_b_to_a_exchange_fee_rate(self) -> float:
        return self.alpha

    def process_trade(self, balance_change: BalanceChange):
        self.liquidity_state.process_trade(balance_change)
