from dataclasses import dataclass
import logging

from balance_change import BalanceChange
from fee_algorithm.base import TradeSizeAwareFeeAlgorithm
from pool.liquidity_state import PoolLiquidityState
import numpy as np
from user_action import construct_user_swap_a_to_b
from prices_snapshot import PricesSnapshot


@dataclass
class ZeroILFee(TradeSizeAwareFeeAlgorithm):
    # These fields keep the most recently observed directional fee for logging
    # and notebook visualizations. The current-trade fee is computed exactly
    # from the incoming order size via get_a_to_b_trade_fee(...).
    a_to_b_exchange_fee_rate: float = 0.003
    b_to_a_exchange_fee_rate: float = 0.003

    def get_a_to_b_trade_fee(
        self, pool_state: PoolLiquidityState, x_user: float
    ) -> float:
        assert x_user >= 0
        assert pool_state.quantity_a > 0

        alpha = x_user / pool_state.quantity_a
        fee_rate = alpha / (1 + alpha)

        # Compute the fee in a numerically stable way:
        # phi * x = x^2 / (x0 + x), which guarantees fee_paid <= x_user.
        fee_paid = (x_user * x_user) / (pool_state.quantity_a + x_user)
        fee_paid = min(max(fee_paid, 0.0), x_user)

        self.a_to_b_exchange_fee_rate = fee_rate
        return fee_paid

    def process_trade(
        self, pool_balance_change: BalanceChange, pool_state: PoolLiquidityState
    ) -> None:
        if pool_balance_change.delta_x > 0:
            self.b_to_a_exchange_fee_rate = 0
        elif pool_balance_change.delta_y > 0:
            self.a_to_b_exchange_fee_rate = 0

        logging.info(
            f"Updated fees: a -> b={self.a_to_b_exchange_fee_rate}, b -> a={self.b_to_a_exchange_fee_rate}"
        )

    def process_oracle_price(self, a_to_b_price: float) -> None:
        pass

    def get_optimal_a_to_b_swap(
        self,
        pool_state: PoolLiquidityState,
        network_fee: float,
        prices: PricesSnapshot,
    ) -> float | None:
        x = pool_state.quantity_a
        candidates = np.linspace(0, 10 * x, 1000)

        best_markout = -np.inf
        optimal_delta_x = None
        for delta_x in candidates:
            action = construct_user_swap_a_to_b(
                pool_state=pool_state,
                fee_algo=self,
                amount_to_exchange_A=delta_x,
                network_fee=network_fee,
            )
            markout = action.get_user_markout(prices)
            if markout > best_markout:
                best_markout = markout
                optimal_delta_x = delta_x

        return optimal_delta_x

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
