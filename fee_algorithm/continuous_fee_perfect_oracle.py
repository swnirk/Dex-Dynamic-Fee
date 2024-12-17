from dataclasses import dataclass
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
from typing import Optional
from fee_algorithm.base import FeeAlgorithm


@dataclass
class ContinuousFeePerfectOracle(FeeAlgorithm):
    default_fee_rate: float
    oracle_a_to_b_price: Optional[float] = None

    def process_oracle_price(self, a_to_b_price: float) -> None:
        self.oracle_a_to_b_price = a_to_b_price

    def get_a_to_b_trade_fee(self, pool_state: PoolLiquidityState, x_user: float):
        assert self.oracle_a_to_b_price is not None, "Oracle price is not set"

        x_old = pool_state.quantity_a
        y_old = pool_state.quantity_b
        oracle = self.oracle_a_to_b_price
        r = self.default_fee_rate

        a_coef = oracle
        b_coef = x_old * oracle + r * y_old - x_user * oracle
        c_coef = -x_user * x_old * oracle

        x_1 = (-b_coef + (b_coef**2 - 4 * a_coef * c_coef) ** 0.5) / (2 * a_coef)
        x_2 = (-b_coef - (b_coef**2 - 4 * a_coef * c_coef) ** 0.5) / (2 * a_coef)

        # TODO: I have no idea why this holds, need to add formal proof to the paper
        assert x_1 * x_2 <= 0, f"All roots have the same sign: {x_1}, {x_2}"
        assert x_1 >= 0, f"Root x_2 is negative: {x_2}"

        x_to_reach_amm = x_1

        return x_user - x_to_reach_amm

    def process_trade(self, _: BalanceChange) -> None:
        pass

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    def process_block_end(self, pool_state: PoolLiquidityState) -> None:
        pass

    def inverse(self) -> "ContinuousFeePerfectOracle":
        return ContinuousFeePerfectOracle(
            default_fee_rate=self.default_fee_rate,
            oracle_a_to_b_price=(
                1 / self.oracle_a_to_b_price
                if self.oracle_a_to_b_price is not None
                else None
            ),
        )
