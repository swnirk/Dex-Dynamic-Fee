from dataclasses import dataclass
from fee_algorithm.base import FeeUnknownBeforeTradeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
import logging
import numpy as np


@dataclass
class BasedOnTradeVolumeFee(FeeUnknownBeforeTradeAlgorithm):
    a_to_b_exchange_fee_rate: float
    b_to_a_exchange_fee_rate: float

    fee_min: float = 0.001
    fee_max: float = 0.005
    z0: float = 0.01

    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        return self.a_to_b_exchange_fee_rate
    
    def process_oracle_price(self, a_to_b_price: float) -> None:
        pass

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    def process_block_end(self, prev_quantity_a: float, prev_quantity_b: float, pool_state: PoolLiquidityState) -> None:
        pass

    def inverse(self) -> "BasedOnTradeVolumeFee":
        return BasedOnTradeVolumeFee(
            a_to_b_exchange_fee_rate=self.b_to_a_exchange_fee_rate,
            b_to_a_exchange_fee_rate=self.a_to_b_exchange_fee_rate,
            fee_min=self.fee_min,
            fee_max=self.fee_max,
            z0=self.z0,
        )

    def process_trade(self, pool_balance_change: BalanceChange, pool_state: PoolLiquidityState) -> None:
        ratio_x = abs(pool_balance_change.delta_x) / pool_state.quantity_a
        self.a_to_b_exchange_fee_rate = self.fee_min + (self.fee_max - self.fee_min) / (1 + np.exp(-(ratio_x - self.z0)))

        ratio_y = abs(pool_balance_change.delta_y) / pool_state.quantity_b
        self.b_to_a_exchange_fee_rate = self.fee_min + (self.fee_max - self.fee_min) / (1 + np.exp(-(ratio_y - self.z0)))

        logging.info(
            f"Updated fees: a_to_b_exchange_fee_rate={self.a_to_b_exchange_fee_rate}, b_to_a_exchange_fee_rate={self.b_to_a_exchange_fee_rate}"
        )
