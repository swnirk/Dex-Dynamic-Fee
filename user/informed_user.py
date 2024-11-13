import numpy as np
from user.abstract_user import (
    User,
    UserAction,
    construct_user_swap_a_to_b,
    validate_user_action,
)
from typing import Optional
import logging
from pool.abstract_pool import Pool
from prices_snapshot import PricesSnapshot


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
            action = UserAction(action.delta_y, action.delta_x, action.fee)
        else:
            return None

        logging.debug(f"User action: {action}")

        validate_user_action(pool.liquidity_state, action)

        return action

    def _get_optimal_a_to_b_swap(
        self,
        pool: Pool,
        network_fee: float,
        prices: PricesSnapshot,
    ) -> UserAction:
        x = pool.liquidity_state.quantity_a
        y = pool.liquidity_state.quantity_b
        alpha = pool.get_a_to_b_exchange_fee_rate()

        q = prices.price_a / prices.price_b
        beta = 1 - alpha

        assert pool.get_a_to_b_exchange_price() > q

        # In terms of "pool" balance;
        # So, if optimal_delta_x is 1, than optimal action is increasing pool's x-balance by 1 and thus selling 1 unit of x
        optimal_delta_x = (np.sqrt(x * y / q) - x) / beta

        assert optimal_delta_x >= 0

        logging.debug(f"Optimal delta x: {optimal_delta_x}")

        action = construct_user_swap_a_to_b(
            pool.liquidity_state,
            pool.get_a_to_b_exchange_fee_rate(),
            prices,
            optimal_delta_x,
        )

        return action
