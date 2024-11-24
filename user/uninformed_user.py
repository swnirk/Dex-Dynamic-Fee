import numpy as np
from user.abstract_user import (
    User,
    UserAction,
    construct_user_swap_a_to_b,
    validate_user_action,
)
from common import (
    capital_function,
)
from typing import Optional
from pool.abstract_pool import Pool
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
                action = UserAction(action.delta_y, action.delta_x, action.fee)

        if action is None:
            return None

        validate_user_action(pool.liquidity_state, action)
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

        # User side
        fee = pool.get_a_to_b_exchange_fee_rate()

        action = construct_user_swap_a_to_b(
            pool.liquidity_state,
            fee,
            prices,
            delta_x,
        )
        action_no_fee = construct_user_swap_a_to_b(
            pool.liquidity_state, 0, prices, delta_x
        )

        delta_P = capital_function(action.delta_x, action.delta_y, prices)
        delta_P_no_fee = capital_function(
            action_no_fee.delta_x, action_no_fee.delta_y, prices
        )

        r = delta_P / delta_P_no_fee

        assert r <= 1

        probability_of_trade = np.exp(-abs(r))
        random_value = np.random.rand()

        if random_value > probability_of_trade:
            return None

        return action
