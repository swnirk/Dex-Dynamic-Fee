from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from balance_change import BalanceChange
from fee_algorithm.base import FeeAlgorithm, TradeSizeAwareFeeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from prices_snapshot import PricesSnapshot


@dataclass
class PiecewiseFee(TradeSizeAwareFeeAlgorithm):
    """Wrapper that applies ZeroIL fee in the arbitrage direction
    and delegates to the base algorithm otherwise.

    Arbitrage direction for A->B: pool_a_to_b_price > oracle_a_to_b_price
    (i.e. A is overpriced in the pool relative to oracle).
    """

    base_algorithm: FeeAlgorithm = field(default=None)
    oracle_a_to_b_price: Optional[float] = None

    a_to_b_exchange_fee_rate: float = 0.003
    b_to_a_exchange_fee_rate: float = 0.003

    def _is_arbitrage_direction(self, pool_state: PoolLiquidityState) -> bool:
        if self.oracle_a_to_b_price is None:
            return False
        return pool_state.get_a_to_b_exchange_price() > self.oracle_a_to_b_price

    @staticmethod
    def _zero_il_fee(x_user: float, quantity_a: float) -> float:
        # Compute the fee in a numerically stable way:
        # phi * x = x^2 / (x0 + x), which guarantees fee_paid <= x_user.
        fee_paid = (x_user * x_user) / (quantity_a + x_user)
        return min(max(fee_paid, 0.0), x_user)

    def get_a_to_b_trade_fee(
        self, pool_state: PoolLiquidityState, x_user: float
    ) -> float:
        base_fee = self.base_algorithm.get_a_to_b_trade_fee(pool_state, x_user)
        if self._is_arbitrage_direction(pool_state):
            zero_il_fee = self._zero_il_fee(x_user, pool_state.quantity_a)
            fee = max(base_fee, zero_il_fee)
        else:
            fee = base_fee
        self.a_to_b_exchange_fee_rate = fee / x_user if x_user > 0 else 0.0
        return fee

    def get_optimal_a_to_b_swap(
        self,
        pool_state: PoolLiquidityState,
        network_fee: float,
        prices: PricesSnapshot,
    ) -> Optional[float]:
        x = pool_state.quantity_a
        y = pool_state.quantity_b
        q = prices.price_a / prices.price_b
        return (np.sqrt(x * y / q) - x) / 2

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        self.base_algorithm.process_initial_pool_state(pool_state)

    def process_trade(
        self, pool_balance_change: BalanceChange, pool_state: PoolLiquidityState
    ) -> None:
        if pool_balance_change.delta_x > 0:
            self.b_to_a_exchange_fee_rate = 0
        elif pool_balance_change.delta_y > 0:
            self.a_to_b_exchange_fee_rate = 0
        self.base_algorithm.process_trade(pool_balance_change, pool_state)

    def process_oracle_price(self, a_to_b_price: float) -> None:
        self.oracle_a_to_b_price = a_to_b_price
        self.base_algorithm.process_oracle_price(a_to_b_price)

    def process_block_end(
        self,
        prev_quantity_a: float,
        prev_quantity_b: float,
        pool_state: PoolLiquidityState,
    ) -> None:
        self.base_algorithm.process_block_end(
            prev_quantity_a, prev_quantity_b, pool_state
        )

    def inverse(self) -> "PiecewiseFee":
        return PiecewiseFee(
            base_algorithm=self.base_algorithm.inverse(),
            oracle_a_to_b_price=(
                1 / self.oracle_a_to_b_price
                if self.oracle_a_to_b_price is not None
                else None
            ),
            a_to_b_exchange_fee_rate=self.b_to_a_exchange_fee_rate,
            b_to_a_exchange_fee_rate=self.a_to_b_exchange_fee_rate,
        )
