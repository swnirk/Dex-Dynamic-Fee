from dataclasses import dataclass
from fee_algorithm.base import FeeKnownBeforeTradeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
import logging


@dataclass
class AMMforAMMfee(FeeKnownBeforeTradeAlgorithm):
    a_to_b_exchange_fee_rate: float
    b_to_a_exchange_fee_rate: float

    A: float = 1e8
    k: float = 0.006

    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        return self.a_to_b_exchange_fee_rate

    def process_oracle_price(self, a_to_b_price: float) -> None:
        pass

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    def process_block_end(self, prev_quantity_a: float, prev_quantity_b: float, pool_state: PoolLiquidityState) -> None:
        prev_DEX_p = prev_quantity_a / prev_quantity_b
        cur_DEX_p = pool_state.quantity_a / pool_state.quantity_b
        delta = cur_DEX_p - prev_DEX_p
        # print(delta)
        # self.b_to_a_exchange_fee_rate += delta*self.A
        # if self.b_to_a_exchange_fee_rate <= 0.0:
        #     self.b_to_a_exchange_fee_rate = 0.0001
        # if self.b_to_a_exchange_fee_rate >= 0.006:
        #     self.b_to_a_exchange_fee_rate = 0.0059
        # self.a_to_b_exchange_fee_rate = self.k - self.b_to_a_exchange_fee_rate

        self.a_to_b_exchange_fee_rate += delta*self.A
        if self.a_to_b_exchange_fee_rate <= 0.0:
            self.a_to_b_exchange_fee_rate = 0.0001
        if self.a_to_b_exchange_fee_rate >= 0.006:
            self.a_to_b_exchange_fee_rate = 0.0059
        self.b_to_a_exchange_fee_rate = self.k - self.a_to_b_exchange_fee_rate

    def inverse(self) -> "AMMforAMMfee":
        return AMMforAMMfee(
            a_to_b_exchange_fee_rate=self.b_to_a_exchange_fee_rate,
            b_to_a_exchange_fee_rate=self.a_to_b_exchange_fee_rate,
            A=self.A,
            k=self.k
        )

    def process_trade(self, pool_balance_change: BalanceChange, pool_state: PoolLiquidityState) -> None:
        pass

        logging.info(
            f"Updated fees: a_to_b_exchange_fee_rate={self.a_to_b_exchange_fee_rate}, b_to_a_exchange_fee_rate={self.b_to_a_exchange_fee_rate}"
        )
