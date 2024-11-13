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


class UninformedUser(User):
    def get_user_action(
        self,
        pool: Pool,
        network_fee: float,
        fair_price_A: float,
        fair_price_B: float,
    ) -> Optional[UserAction]:
        if fair_price_A > fair_price_B:
            p_token_1 = 0.6
        else:
            p_token_1 = 0.4
        token_choice = np.random.choice(
            ["token1", "token2"], size=1, p=[p_token_1, 1 - p_token_1]
        )

        action: Optional[UserAction] = None

        if token_choice == "token1":
            action = self._get_a_to_b_swap(
                pool,
                fair_price_A,
                fair_price_B,
            )
        else:
            action = self._get_a_to_b_swap(
                pool.inverse_pool(),
                fair_price_B,
                fair_price_A,
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
        fair_price_A: float,
        fair_price_B: float,
    ) -> Optional[UserAction]:
        mu = 0.0005
        sigma = 0.0001
        share = np.random.normal(mu, sigma)

        # "Pool" side;
        delta_x = share * pool.liquidity_state.quantity_a

        if share == 0:
            return None

        # User side
        action = construct_user_swap_a_to_b(
            pool.liquidity_state,
            pool.get_a_to_b_exchange_fee_rate(),
            fair_price_A,
            fair_price_B,
            delta_x,
        )
        action_no_fee = construct_user_swap_a_to_b(
            pool.liquidity_state, 0, fair_price_A, fair_price_B, delta_x
        )

        delta_P = capital_function(
            action.delta_x, action.delta_y, fair_price_A, fair_price_B
        )
        delta_P_no_fee = capital_function(
            action_no_fee.delta_x, action_no_fee.delta_y, fair_price_A, fair_price_B
        )

        r = delta_P / delta_P_no_fee

        assert r <= 1

        probability_of_trade = np.exp(-abs(r))
        random_value = np.random.rand()

        if random_value > probability_of_trade:
            return None

        return action
