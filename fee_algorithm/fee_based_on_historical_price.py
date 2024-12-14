from dataclasses import dataclass
from fee_algorithm.base import FeeKnownBeforeTradeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
from typing import Optional
from exponential_counter import ExponentialCounter


@dataclass
class FeeBasedOnHistoricalPrice(FeeKnownBeforeTradeAlgorithm):
    decay: float

    fee_in_increasing_deviation_direction: float
    fee_in_decreasing_deviation_direction: float

    a_t_b_price_exponential_counter: Optional[ExponentialCounter] = None
    b_to_a_price_exponential_counter: Optional[ExponentialCounter] = None

    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        assert self.a_t_b_price_exponential_counter is not None
        if (
            pool_state.get_a_to_b_exchange_price()
            > self.a_t_b_price_exponential_counter.get_value()
        ):
            return self.fee_in_increasing_deviation_direction
        else:
            return self.fee_in_decreasing_deviation_direction

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        self.a_t_b_price_exponential_counter = ExponentialCounter(
            decay=self.decay, initial_value=pool_state.get_a_to_b_exchange_price()
        )
        self.b_to_a_price_exponential_counter = ExponentialCounter(
            decay=self.decay, initial_value=pool_state.get_b_to_a_exchange_price()
        )

    def process_trade(self, pool_balance_change: BalanceChange) -> None:
        pass

    def process_oracle_price(self, a_to_b_price: float):
        pass

    def process_block_end(self, pool_state: PoolLiquidityState) -> None:
        assert self.a_t_b_price_exponential_counter is not None
        assert self.b_to_a_price_exponential_counter is not None
        self.a_t_b_price_exponential_counter.update(
            pool_state.get_a_to_b_exchange_price()
        )
        self.b_to_a_price_exponential_counter.update(
            pool_state.get_b_to_a_exchange_price()
        )

    def inverse(self) -> "FeeBasedOnHistoricalPrice":
        return FeeBasedOnHistoricalPrice(
            decay=self.decay,
            fee_in_increasing_deviation_direction=self.fee_in_increasing_deviation_direction,
            fee_in_decreasing_deviation_direction=self.fee_in_decreasing_deviation_direction,
            a_t_b_price_exponential_counter=self.b_to_a_price_exponential_counter,
            b_to_a_price_exponential_counter=self.a_t_b_price_exponential_counter,
        )
