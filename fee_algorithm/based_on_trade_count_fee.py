from dataclasses import dataclass
from fee_algorithm.base import FeeKnownBeforeTradeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
import logging


@dataclass
class BasedOnTradeCountFee(FeeKnownBeforeTradeAlgorithm):
    a_to_b_exchange_fee_rate: float
    b_to_a_exchange_fee_rate: float

    a_to_b_trade_count: int = 0
    b_to_a_trade_count: int = 0

    fee_step: float = 0.0001  # 1 bps

    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        return self.a_to_b_exchange_fee_rate

    def process_oracle_price(self, a_to_b_price: float) -> None:
        pass

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    def process_block_end(self, pool_state: PoolLiquidityState) -> None:
        pass

    def inverse(self) -> "BasedOnTradeCountFee":
        return BasedOnTradeCountFee(
            a_to_b_exchange_fee_rate=self.b_to_a_exchange_fee_rate,
            b_to_a_exchange_fee_rate=self.a_to_b_exchange_fee_rate,
            a_to_b_trade_count=self.b_to_a_trade_count,
            b_to_a_trade_count=self.a_to_b_trade_count,
            fee_step=self.fee_step,
        )

    def process_trade(self, pool_balance_change: BalanceChange) -> None:
        delta_a = pool_balance_change.delta_x
        delta_b = pool_balance_change.delta_y

        if delta_a < 0:
            self.a_to_b_trade_count += 1
        elif delta_b < 0:
            self.b_to_a_trade_count += 1

        delta = self.a_to_b_trade_count - self.b_to_a_trade_count
        # if abs(delta) > 5:
        #     if delta > 0 and self.b_to_a_exchange_fee_rate >= self.fee_step:
        #         self.a_to_b_exchange_fee_rate += self.fee_step
        #         self.b_to_a_exchange_fee_rate -= self.fee_step
        #     elif delta < 0 and self.a_to_b_exchange_fee_rate >= self.fee_step:
        #         self.b_to_a_exchange_fee_rate += self.fee_step
        #         self.a_to_b_exchange_fee_rate -= self.fee_step

        # if delta > 0 and self.a_to_b_exchange_fee_rate < 0.20:
        if delta_a < 0 and self.a_to_b_exchange_fee_rate < 0.20:
            self.a_to_b_exchange_fee_rate += self.fee_step
            if self.b_to_a_exchange_fee_rate > self.fee_step:
                self.b_to_a_exchange_fee_rate -= self.fee_step
        elif delta_b < 0 and self.b_to_a_exchange_fee_rate < 0.20:
            self.b_to_a_exchange_fee_rate += self.fee_step
            if self.a_to_b_exchange_fee_rate > self.fee_step:
                self.a_to_b_exchange_fee_rate -= self.fee_step

        logging.info(
            f"Updated fees: a_to_b_exchange_fee_rate={self.a_to_b_exchange_fee_rate}, b_to_a_exchange_fee_rate={self.b_to_a_exchange_fee_rate}, "
            f"a_to_b_trade_count={self.a_to_b_trade_count}, b_to_a_trade_count={self.b_to_a_trade_count}"
        )
