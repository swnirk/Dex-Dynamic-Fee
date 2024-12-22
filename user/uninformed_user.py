import numpy as np
from user.abstract_user import (
    User,
    UserAction,
)
from user_action import construct_user_swap_a_to_b
from typing import Optional
from pool.pool import Pool
from prices_snapshot import PricesSnapshot
from common import capital_function


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
                network_fee,
            )
        else:
            action = self._get_a_to_b_swap(
                pool.inverse_pool(),
                prices.inverse(),
                network_fee,
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
        network_fee: float,
    ) -> Optional[UserAction]:
        # mu = 0.00005
        mu = 0.00016
        # sigma = 0.00001
        sigma = 0.00001
        share = np.random.normal(mu, sigma)

        # "Pool" side;
        delta_x = share * pool.liquidity_state.quantity_a

        if share == 0:
            return None

        action = construct_user_swap_a_to_b(
            pool.liquidity_state,
            pool.fee_algorithm,
            amount_to_exchange_A=delta_x,
            network_fee=network_fee,
        )

        user_balance_change = action.get_user_balance_change()
        user_profit = capital_function(user_balance_change.delta_x, user_balance_change.delta_y, prices)
        total_change = capital_function(abs(user_balance_change.delta_x), abs(user_balance_change.delta_y), prices)
        r = user_profit / total_change
        if r > 0:
            return action
        else:
            trade_probability = np.exp(-abs(r))
            random_value = np.random.rand()

            if random_value < trade_probability:
                return action
            else:
                return None