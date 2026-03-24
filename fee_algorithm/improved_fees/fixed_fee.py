from dataclasses import dataclass
from typing import Optional

import numpy as np

from balance_change import BalanceChange
from fee_algorithm.base import TradeSizeAwareFeeAlgorithm
from pool.liquidity_state import PoolLiquidityState
from prices_snapshot import PricesSnapshot


@dataclass
class ImprovedFixedFee(TradeSizeAwareFeeAlgorithm):
    """Piecewise fee: fixed fee while alpha < phi_1 + phi_2 (IG region),
    ZeroIL fee when alpha >= phi_1 + phi_2 (IL region).

    phi_1: fee rate for A -> B direction
    phi_2: fee rate for B -> A direction
    """

    phi_1: float = 0.003
    phi_2: float = 0.003

    a_to_b_exchange_fee_rate: float = 0.003
    b_to_a_exchange_fee_rate: float = 0.003

    def get_a_to_b_trade_fee(
        self, pool_state: PoolLiquidityState, x_user: float
    ) -> float:
        fixed_fee = self.phi_1 * x_user
        # ZeroIL: fee = x^2 / (x0 + x)
        zero_il_fee = (x_user * x_user) / (pool_state.quantity_a + x_user)
        zero_il_fee = min(max(zero_il_fee, 0.0), x_user)

        fee = max(fixed_fee, zero_il_fee)

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
        boundary = self.phi_1 + self.phi_2

        # Fixed fee optimal swap
        beta = 1 - self.phi_1
        fixed_opt = (np.sqrt(x * y * beta / q) - x) / beta

        if fixed_opt is None or fixed_opt < 0:
            return None

        alpha_fixed = fixed_opt / x
        if alpha_fixed < boundary:
            # Optimal trade lands in the fixed fee region
            return fixed_opt

        # ZeroIL optimal swap
        zero_il_opt = (np.sqrt(x * y / q) - x) / 2
        if zero_il_opt is not None and zero_il_opt > 0:
            return zero_il_opt

        return None

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    def process_trade(
        self, pool_balance_change: BalanceChange, pool_state: PoolLiquidityState
    ) -> None:
        if pool_balance_change.delta_x > 0:
            self.b_to_a_exchange_fee_rate = 0
        elif pool_balance_change.delta_y > 0:
            self.a_to_b_exchange_fee_rate = 0

    def process_oracle_price(self, a_to_b_price: float) -> None:
        pass

    def process_block_end(
        self,
        prev_quantity_a: float,
        prev_quantity_b: float,
        pool_state: PoolLiquidityState,
    ) -> None:
        pass

    def inverse(self) -> "ImprovedFixedFee":
        return ImprovedFixedFee(
            phi_1=self.phi_2,
            phi_2=self.phi_1,
            a_to_b_exchange_fee_rate=self.b_to_a_exchange_fee_rate,
            b_to_a_exchange_fee_rate=self.a_to_b_exchange_fee_rate,
        )
