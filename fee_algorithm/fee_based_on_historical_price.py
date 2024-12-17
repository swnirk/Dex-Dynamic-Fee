from dataclasses import dataclass
from fee_algorithm.base import FeeKnownBeforeTradeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
from typing import Optional
from exponential_moving_average import ExponentialMovingAverage


@dataclass
class FeeBasedOnHistoricalPrice(FeeKnownBeforeTradeAlgorithm):
    alpha: float

    fee_in_increasing_deviation_direction: float
    fee_in_decreasing_deviation_direction: float

    a_to_b_price_ema: Optional[ExponentialMovingAverage] = None
    b_to_a_price_ema: Optional[ExponentialMovingAverage] = None

    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        assert self.a_to_b_price_ema is not None
        if pool_state.get_a_to_b_exchange_price() > self.a_to_b_price_ema.average():
            return self.fee_in_increasing_deviation_direction
        else:
            return self.fee_in_decreasing_deviation_direction

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        self.a_to_b_price_ema = ExponentialMovingAverage(
            alpha=self.alpha, initial_value=pool_state.get_a_to_b_exchange_price()
        )
        self.b_to_a_price_ema = ExponentialMovingAverage(
            alpha=self.alpha, initial_value=pool_state.get_b_to_a_exchange_price()
        )

    def process_trade(self, pool_balance_change: BalanceChange) -> None:
        pass

    def process_oracle_price(self, a_to_b_price: float):
        pass

    def process_block_end(self, pool_state: PoolLiquidityState) -> None:
        assert self.a_to_b_price_ema is not None
        assert self.b_to_a_price_ema is not None
        self.a_to_b_price_ema.update(pool_state.get_a_to_b_exchange_price())
        self.b_to_a_price_ema.update(pool_state.get_b_to_a_exchange_price())

    def inverse(self) -> "FeeBasedOnHistoricalPrice":
        return FeeBasedOnHistoricalPrice(
            alpha=self.alpha,
            fee_in_increasing_deviation_direction=self.fee_in_increasing_deviation_direction,
            fee_in_decreasing_deviation_direction=self.fee_in_decreasing_deviation_direction,
            a_to_b_price_ema=self.b_to_a_price_ema,
            b_to_a_price_ema=self.a_to_b_price_ema,
        )
