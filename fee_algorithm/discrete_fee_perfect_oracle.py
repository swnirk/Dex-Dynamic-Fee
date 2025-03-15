from dataclasses import dataclass
from fee_algorithm.base import FeeKnownBeforeTradeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
from typing import Optional


@dataclass
class DiscreteFeePerfectOracle(FeeKnownBeforeTradeAlgorithm):
    fee_rate_in_arbitrage_direction: float
    fee_rate_in_non_arbitrage_direction: float

    oracle_a_to_b_price: Optional[float] = None

    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        assert self.oracle_a_to_b_price is not None, "Oracle price is not set"
        if pool_state.get_a_to_b_exchange_price() > self.oracle_a_to_b_price:
            return self.fee_rate_in_arbitrage_direction
        else:
            return self.fee_rate_in_non_arbitrage_direction

    def process_oracle_price(self, a_to_b_price: float):
        self.oracle_a_to_b_price = a_to_b_price

    def process_trade(self, balance_change: BalanceChange, pool_state: PoolLiquidityState):
        pass

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    def process_block_end(self, prev_quantity_a: float, prev_quantity_b: float, pool_state: PoolLiquidityState) -> None:
        pass

    def inverse(self) -> "DiscreteFeePerfectOracle":
        return DiscreteFeePerfectOracle(
            fee_rate_in_arbitrage_direction=self.fee_rate_in_arbitrage_direction,
            fee_rate_in_non_arbitrage_direction=self.fee_rate_in_non_arbitrage_direction,
            oracle_a_to_b_price=(
                1 / self.oracle_a_to_b_price
                if self.oracle_a_to_b_price is not None
                else None
            ),
        )
