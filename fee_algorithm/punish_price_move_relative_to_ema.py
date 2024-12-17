from fee_algorithm.base import FeeAlgorithm
from typing import Optional
from exponential_counter import ExponentialCounter
from pool.liquidity_state import PoolLiquidityState
from balance_change import BalanceChange
from copy import deepcopy
from common import get_amm_exchange_value_a_to_b
from dataclasses import dataclass

# TODO: Figure out if it is possible to support this fee algorithm in InformedUser
# Looks like there is no closed-form solution for the optimal action


@dataclass
class PunishPriceMoveRelativeToEmaIncludingCurrentTradeFee(FeeAlgorithm):
    base_fee: float
    decay: float

    a_t_b_price_exponential_counter: Optional[ExponentialCounter] = None
    b_to_a_price_exponential_counter: Optional[ExponentialCounter] = None

    def get_a_to_b_trade_fee(
        self, pool_state: PoolLiquidityState, x_user: float
    ) -> float:
        assert self.a_t_b_price_exponential_counter is not None

        pool_after_deal = deepcopy(pool_state)
        y_user = get_amm_exchange_value_a_to_b(
            pool_state.quantity_a, pool_state.quantity_b, x_user
        )
        pool_after_deal.process_trade(BalanceChange(x_user, y_user))

        current_price_ema = self.a_t_b_price_exponential_counter.get_value()
        price_after_deal = pool_after_deal.get_a_to_b_exchange_price()

        ratio = price_after_deal / current_price_ema

        return self.base_fee * ratio * x_user

    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        self.a_t_b_price_exponential_counter = ExponentialCounter(
            decay=self.decay, initial_value=pool_state.get_a_to_b_exchange_price()
        )
        self.b_to_a_price_exponential_counter = ExponentialCounter(
            decay=self.decay, initial_value=pool_state.get_b_to_a_exchange_price()
        )

    def process_trade(self, pool_balance_change: BalanceChange) -> None:
        pass

    def process_oracle_price(self, a_to_b_price: float):
        pass

    def process_block_end(self, pool_state: PoolLiquidityState) -> None:
        assert self.a_t_b_price_exponential_counter is not None
        assert self.b_to_a_price_exponential_counter is not None
        self.a_t_b_price_exponential_counter.update(
            pool_state.get_a_to_b_exchange_price()
        )
        self.b_to_a_price_exponential_counter.update(
            pool_state.get_b_to_a_exchange_price()
        )

    def inverse(self) -> "PunishPriceMoveRelativeToEmaIncludingCurrentTradeFee":
        return PunishPriceMoveRelativeToEmaIncludingCurrentTradeFee(
            decay=self.decay,
            base_fee=self.base_fee,
            a_t_b_price_exponential_counter=self.b_to_a_price_exponential_counter,
            b_to_a_price_exponential_counter=self.a_t_b_price_exponential_counter,
        )
