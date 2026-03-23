from dataclasses import dataclass
from fee_algorithm.base import FeeKnownBeforeTradeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
import logging


@dataclass
class ZeroILFee(FeeKnownBeforeTradeAlgorithm):
    a_to_b_exchange_fee_rate: float = 0.003
    b_to_a_exchange_fee_rate: float = 0.003

    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        return self.a_to_b_exchange_fee_rate

    def process_trade(
        self, pool_balance_change: BalanceChange, pool_state: PoolLiquidityState
    ) -> None:
        delta_a = pool_balance_change.delta_x
        delta_b = pool_balance_change.delta_y

        if delta_a > 0:  # swap a to b
            alpha = delta_a / pool_state.quantity_a
            self.a_to_b_exchange_fee_rate = alpha / (1 + alpha)
            self.b_to_a_exchange_fee_rate = 0
        elif delta_b > 0:  # swap b to a
            alpha = delta_b / pool_state.quantity_b
            self.b_to_a_exchange_fee_rate = alpha / (1 + alpha)
            self.a_to_b_exchange_fee_rate = 0

        logging.info(
            f"Updated fees: a -> b={self.a_to_b_exchange_fee_rate}, b -> a={self.b_to_a_exchange_fee_rate}"
        )

    def process_oracle_price(self, a_to_b_price: float):
        pass

    def inverse(self) -> "ZeroILFee":
        return ZeroILFee(
            a_to_b_exchange_fee_rate=self.b_to_a_exchange_fee_rate,
            b_to_a_exchange_fee_rate=self.a_to_b_exchange_fee_rate,
        )

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    def process_block_end(
        self,
        prev_quantity_a: float,
        prev_quantity_b: float,
        pool_state: PoolLiquidityState,
    ) -> None:
        pass
