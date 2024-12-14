from dataclasses import dataclass
from fee_algorithm.base import FeeKnownBeforeTradeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange


@dataclass
class FixedFee(FeeKnownBeforeTradeAlgorithm):
    exchange_fee_rate: float

    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        return self.exchange_fee_rate

    def process_trade(self, pool_balance_change: BalanceChange) -> None:
        pass

    def process_oracle_price(self, a_to_b_price: float):
        pass

    def inverse(self) -> "FixedFee":
        return self

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    def process_block_end(self, pool_state: PoolLiquidityState) -> None:
        pass
