import numpy as np
from user.abstract_user import (
    User,
    UserAction,
)
from user_action import construct_user_swap_a_to_b
from typing import Optional
import logging
from pool.pool import Pool
from prices_snapshot import PricesSnapshot
from user_action import construct_user_swap_b_to_a
from dataclasses import dataclass


@dataclass
class InformedUserBruteforce(User):
    n_samples: int = 1000

    def get_user_action(
        self,
        pool: Pool,
        network_fee: float,
        prices: PricesSnapshot,
    ) -> Optional[UserAction]:
        possible_actions: list[tuple[UserAction, float]] = []

        def _process_action(action: UserAction):
            markout = action.get_user_markout(prices)
            possible_actions.append((action, markout))

        for amount_to_exchange_A in np.linspace(
            0, 10 * pool.liquidity_state.quantity_a, self.n_samples
        ):
            action = construct_user_swap_a_to_b(
                pool.liquidity_state,
                pool.fee_algorithm,
                amount_to_exchange_A=amount_to_exchange_A,
                network_fee=network_fee,
            )
            _process_action(action)

        for amount_to_exchange_B in np.linspace(
            0, 10 * pool.liquidity_state.quantity_b, self.n_samples
        ):
            action = construct_user_swap_b_to_a(
                pool.liquidity_state,
                pool.fee_algorithm,
                amount_to_exchange_B=amount_to_exchange_B,
                network_fee=network_fee,
            )
            _process_action(action)

        optimal_action, optimal_action_markout = max(
            possible_actions, key=lambda x: x[1]
        )

        if optimal_action_markout < 0:
            return None

        return optimal_action
