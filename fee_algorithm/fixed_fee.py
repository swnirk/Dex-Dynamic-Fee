from dataclasses import dataclass
from fee_algorithm.base import FeeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange


@dataclass
class FixedFee(FeeAlgorithm):
    exchange_fee_rate: float

    def get_a_to_b_exchange_fee_rate(self, _: PoolLiquidityState) -> float:
        return self.exchange_fee_rate

    def get_b_to_a_exchange_fee_rate(self, _: PoolLiquidityState) -> float:
        return self.exchange_fee_rate

    def process_trade(self, pool_balance_change: BalanceChange) -> None:
        pass

    def process_oracle_price(self, a_to_b_price: float):
        pass

    def inverse(self) -> "FeeAlgorithm":
        return self
