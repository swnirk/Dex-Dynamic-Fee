from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from balance_change import BalanceChange
from fee_algorithm.base import FeeAlgorithm, TradeSizeAwareFeeAlgorithm
from fee_algorithm.dynamic_fee_zero_il import ZeroILFee
from pool.liquidity_state import PoolLiquidityState
from prices_snapshot import PricesSnapshot

_zero_il = ZeroILFee()


@dataclass
class PiecewiseFee(TradeSizeAwareFeeAlgorithm):
    """Universal wrapper: treats the base algorithm's current fee rate as
    a per-block fixed fee phi_1, and applies max(phi_1 * x, zero_il_fee).

    Works with any FeeAlgorithm that exposes get_a_to_b_exchange_fee_rate
    (i.e. FeeKnownBeforeTradeAlgorithm, FeeUnknownBeforeTradeAlgorithm).
    """

    base_algorithm: FeeAlgorithm = field(default=None)

    a_to_b_exchange_fee_rate: float = 0.003
    b_to_a_exchange_fee_rate: float = 0.003

    def _get_base_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        """Get current fee rate from the base algorithm."""
        return self.base_algorithm.get_a_to_b_exchange_fee_rate(pool_state)

    def _get_base_inverse_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        """Get fee rate for the inverse direction from the base algorithm."""
        return self.base_algorithm.inverse().get_a_to_b_exchange_fee_rate(
            pool_state.inverse()
        )

    def get_a_to_b_trade_fee(
        self, pool_state: PoolLiquidityState, x_user: float
    ) -> float:
        phi_1 = self._get_base_fee_rate(pool_state)
        phi_2 = self._get_base_inverse_fee_rate(pool_state)
        alpha = x_user / pool_state.quantity_a
        if alpha < phi_1 + phi_2:
            fee = phi_1 * x_user  # IG-регион: фиксированная комиссия
        else:
            fee = _zero_il.get_a_to_b_trade_fee(pool_state, x_user)  # IL-регион
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

        phi_1 = self._get_base_fee_rate(pool_state)
        phi_2 = self._get_base_inverse_fee_rate(pool_state)
        gamma_1 = 1 - phi_1
        gamma_2 = 1 - phi_2
        boundary = phi_1 + phi_2
        boundary = (1 - gamma_1 * gamma_2) / gamma_1 / (2 * gamma_2 - 1)

        # Fixed fee optimal swap
        beta = 1 - phi_1
        fixed_opt = (np.sqrt(x * y * beta / q) - x) / beta

        if fixed_opt <= 0:
            return None

        alpha_fixed = fixed_opt / x
        if alpha_fixed < boundary:
            return fixed_opt

        # ZeroIL optimal swap — reuse proven formula from ZeroILFee
        zero_il_opt = _zero_il.get_optimal_a_to_b_swap(pool_state, network_fee, prices)
        if zero_il_opt is not None and zero_il_opt > 0:
            return zero_il_opt

        return None

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
            a_to_b_exchange_fee_rate=self.b_to_a_exchange_fee_rate,
            b_to_a_exchange_fee_rate=self.a_to_b_exchange_fee_rate,
        )
