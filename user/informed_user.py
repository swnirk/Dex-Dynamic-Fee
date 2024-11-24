import numpy as np
from user.abstract_user import (
    User,
    UserAction,
)
from user_action import construct_user_swap_a_to_b
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
        x = pool.liquidity_state.quantity_a
        y = pool.liquidity_state.quantity_b
        q = prices.price_a / prices.price_b

        fee = pool.get_a_to_b_exchange_fee_rate()
        beta = 1 - fee

        assert pool.get_a_to_b_exchange_price() > q

        # In terms of "pool" balance;
        # So, if optimal_delta_x is 1, than optimal action is increasing pool's x-balance by 1 and thus selling 1 unit of x
        optimal_delta_x = (np.sqrt(x * y * beta / q) - x) / beta

        logging.debug(f"Optimal delta x: {optimal_delta_x}")

        if optimal_delta_x < 0:
            # This may happen when fee is too high for any profitable swap
            return None

        action = construct_user_swap_a_to_b(
            pool.liquidity_state,
            fee,
            optimal_delta_x,
        )

        return action
