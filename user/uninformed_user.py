import numpy as np
from user.abstract_user import (
    User,
    UserAction,
)
from user_action import construct_user_swap_a_to_b
from typing import Optional
from pool.pool import Pool
from prices_snapshot import PricesSnapshot


class UninformedUser(User):
    def get_user_action(
        self,
        pool: Pool,
        network_fee: float,
        prices: PricesSnapshot,
    ) -> Optional[UserAction]:
        token_choice = np.random.choice(["token1", "token2"], size=1, p=[0.5, 0.5])

        action: Optional[UserAction] = None

        if token_choice == "token1":
            action = self._get_a_to_b_swap(
                pool,
                prices,
            )
        else:
            action = self._get_a_to_b_swap(
                pool.inverse_pool(),
                prices.inverse(),
            )
            if action is not None:
                action = action.inverse()

        if action is None:
            return None

        return action

    def _get_a_to_b_swap(
        self,
        pool: Pool,
        prices: PricesSnapshot,
    ) -> Optional[UserAction]:
        mu = 0.0005
        sigma = 0.0001
        share = np.random.normal(mu, sigma)

        # "Pool" side;
        delta_x = share * pool.liquidity_state.quantity_a

        if share == 0:
            return None

        action = construct_user_swap_a_to_b(
            pool.liquidity_state,
            pool.fee_algorithm,
            delta_x,
        )

        return action
