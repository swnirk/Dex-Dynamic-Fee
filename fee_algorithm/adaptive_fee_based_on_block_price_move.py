from dataclasses import dataclass
from fee_algorithm.base import FeeKnownBeforeTradeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
from typing import Optional


@dataclass
class AdaptiveBasedOnPreviousBlockPriceMoveFee(FeeKnownBeforeTradeAlgorithm):
    a_to_b_exchange_fee_rate: float
    b_to_a_exchange_fee_rate: float

    fee_step: float = 0.0001  # 1 bps

    prev_block_begin_a_to_b_price: Optional[float] = None
    prev_block_end_a_to_b_price: Optional[float] = None

    prev_block_begin_b_to_a_price: Optional[float] = None
    prev_block_end_b_to_a_price: Optional[float] = None

    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        return self.a_to_b_exchange_fee_rate

    def process_oracle_price(self, a_to_b_price: float) -> None:
        pass

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        self.prev_block_begin_a_to_b_price = pool_state.get_a_to_b_exchange_price()
        self.prev_block_end_a_to_b_price = pool_state.get_a_to_b_exchange_price()

        self.prev_block_begin_b_to_a_price = pool_state.get_b_to_a_exchange_price()
        self.prev_block_end_b_to_a_price = pool_state.get_b_to_a_exchange_price()

    def process_block_end(self, prev_quantity_a: float, prev_quantity_b: float, pool_state: PoolLiquidityState) -> None:
        assert self.prev_block_end_a_to_b_price is not None
        assert self.prev_block_end_b_to_a_price is not None

        self.prev_block_begin_a_to_b_price = self.prev_block_end_a_to_b_price
        self.prev_block_end_a_to_b_price = pool_state.get_a_to_b_exchange_price()

        self.prev_block_begin_b_to_a_price = self.prev_block_end_b_to_a_price
        self.prev_block_end_b_to_a_price = pool_state.get_b_to_a_exchange_price()

        if (
            self.prev_block_end_a_to_b_price > self.prev_block_begin_a_to_b_price
            and self.a_to_b_exchange_fee_rate >= self.fee_step
        ):
            # (price A / price B) increased -> there were more deals in B->A direction
            # -> we should increase fee for B->A direction
            self.a_to_b_exchange_fee_rate -= self.fee_step
            self.b_to_a_exchange_fee_rate += self.fee_step
        elif (
            self.prev_block_end_a_to_b_price < self.prev_block_begin_a_to_b_price
            and self.b_to_a_exchange_fee_rate >= self.fee_step
        ):
            self.a_to_b_exchange_fee_rate += self.fee_step
            self.b_to_a_exchange_fee_rate -= self.fee_step

    def inverse(self) -> "AdaptiveBasedOnPreviousBlockPriceMoveFee":
        return AdaptiveBasedOnPreviousBlockPriceMoveFee(
            a_to_b_exchange_fee_rate=self.b_to_a_exchange_fee_rate,
            b_to_a_exchange_fee_rate=self.a_to_b_exchange_fee_rate,
            prev_block_begin_a_to_b_price=self.prev_block_begin_b_to_a_price,
            prev_block_end_a_to_b_price=self.prev_block_end_b_to_a_price,
            prev_block_begin_b_to_a_price=self.prev_block_begin_a_to_b_price,
            prev_block_end_b_to_a_price=self.prev_block_end_a_to_b_price,
        )

    def process_trade(self, pool_balance_change: BalanceChange, pool_state: PoolLiquidityState) -> None:
        pass
