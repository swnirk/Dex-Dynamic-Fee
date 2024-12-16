import numpy as np
from user.abstract_user import (
    User,
    UserAction,
)
from user_action import construct_user_swap_a_to_b
from typing import Optional
import logging
from pool.pool import Pool
from pool.liquidity_state import PoolLiquidityState
from prices_snapshot import PricesSnapshot
from fee_algorithm.base import FeeKnownBeforeTradeAlgorithm
from fee_algorithm.fee_based_on_trade import FeeBasedOnTrade


class InformedUser(User):
    def get_user_action(
        self,
        pool: Pool,
        network_fee: float,
        prices: PricesSnapshot,
    ) -> Optional[UserAction]:
        q = prices.price_a / prices.price_b

        action: Optional[UserAction] = None

        if pool.get_a_to_b_exchange_price() > q:
            logging.debug("Users swaps A -> B")
            action = self._get_optimal_a_to_b_swap(
                pool,
                network_fee,
                prices,
            )
        elif pool.get_a_to_b_exchange_price() < q:
            logging.debug("Users swaps B -> A")
            action = self._get_optimal_a_to_b_swap(
                pool.inverse_pool(),
                network_fee,
                prices.inverse(),
            )
            if action is not None:
                action = action.inverse()
        else:
            return None

        logging.debug(f"User action: {action}")

        return action

    def _get_optimal_a_to_b_swap(
        self,
        pool: Pool,
        network_fee: float,
        prices: PricesSnapshot,
    ) -> Optional[UserAction]:
        optimal_delta_x = None

        if isinstance(pool.fee_algorithm, FeeKnownBeforeTradeAlgorithm):
            optimal_delta_x = self._get_optimal_a_to_b_swap_when_fee_known_before_trade(
                pool.liquidity_state,
                prices,
                pool.fee_algorithm.get_a_to_b_exchange_fee_rate(
                    pool_state=pool.liquidity_state
                ),
            )
        elif isinstance(pool.fee_algorithm, FeeBasedOnTrade):
            assert pool.fee_algorithm.oracle_a_to_b_price is not None
            optimal_delta_x = self._get_optimal_a_to_b_swap_fee_based_on_trade(
                pool.liquidity_state,
                prices,
                pool.fee_algorithm.default_fee_rate,
                pool.fee_algorithm.oracle_a_to_b_price,
            )
        else:
            raise NotImplementedError(
                f"Fee algorithm {type(pool.fee_algorithm)} is not supported in InformedUser"
            )

        if optimal_delta_x is None:
            return None

        optimal_action = construct_user_swap_a_to_b(
            pool_state=pool.liquidity_state,
            fee_algo=pool.fee_algorithm,
            amount_to_exchange_A=optimal_delta_x,
            network_fee=network_fee,
        )
        optimal_action_markout = optimal_action.get_user_markout(prices)

        if optimal_action_markout < 0:
            # This may happen when network fee is too high for any profitable swap
            return None

        return optimal_action

    def _get_optimal_a_to_b_swap_when_fee_known_before_trade(
        self,
        liquidity_state: PoolLiquidityState,
        prices: PricesSnapshot,
        fee_rate: float,
    ):
        x = liquidity_state.quantity_a
        y = liquidity_state.quantity_b
        q = prices.price_a / prices.price_b
        fee = fee_rate
        beta = 1 - fee

        assert liquidity_state.get_a_to_b_exchange_price() > q

        # In terms of "pool" balance;
        # So, if optimal_delta_x is 1, than optimal action is increasing pool's x-balance by 1 and thus selling 1 unit of x
        optimal_delta_x = (np.sqrt(x * y * beta / q) - x) / beta

        logging.debug(f"Optimal delta x: {optimal_delta_x}")

        if optimal_delta_x < 0:
            # This may happen when fee rate is too high for any profitable swap
            return None

        return optimal_delta_x

    def _get_optimal_a_to_b_swap_fee_based_on_trade(
        self,
        liquidity_state: PoolLiquidityState,
        prices: PricesSnapshot,
        r: float,
        oracle: float,
    ):
        p1 = prices.price_a
        p2 = prices.price_b
        x_old = liquidity_state.quantity_a
        y_old = liquidity_state.quantity_b

        tmp = p2 * x_old * y_old * oracle - p1 * r * y_old * x_old

        if tmp < 0:
            return None

        x_opt = np.sqrt((tmp) / (p1 * oracle)) - x_old

        if x_opt < 0 or np.isnan(x_opt):
            return None

        x_fee = r * ((x_opt * y_old) / ((x_old + x_opt) * oracle))

        assert x_fee >= 0, f"Fee is negative: x_opt: {x_opt}, x_fee: {x_fee}"

        return x_fee + x_opt
