from dataclasses import dataclass
from fee_algorithm.base import FeeKnownBeforeTradeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
from typing import Optional


@dataclass
class UnequalFee(FeeKnownBeforeTradeAlgorithm):
    fee_rate_in_arbitrage_direction: float
    fee_rate_in_non_arbitrage_direction: float

    oracle_a_to_b_price: Optional[float] = None

    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        assert self.oracle_a_to_b_price is not None, "Oracle price is not set"
        if pool_state.get_a_to_b_exchange_price() > self.oracle_a_to_b_price:
            return self.fee_rate_in_arbitrage_direction
        else:
            return self.fee_rate_in_non_arbitrage_direction

    def get_b_to_a_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        return self.inverse().get_a_to_b_exchange_fee_rate(pool_state.inverse())

    def process_oracle_price(self, a_to_b_price: float):
        self.oracle_a_to_b_price = a_to_b_price

    def process_trade(self, balance_change: BalanceChange):
        pass

    def inverse(self) -> "UnequalFee":
        return UnequalFee(
            fee_rate_in_arbitrage_direction=self.fee_rate_in_arbitrage_direction,
            fee_rate_in_non_arbitrage_direction=self.fee_rate_in_non_arbitrage_direction,
            oracle_a_to_b_price=(
                1 / self.oracle_a_to_b_price
                if self.oracle_a_to_b_price is not None
                else None
            ),
        )
