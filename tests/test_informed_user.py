import pytest

from tests.test_user_action_correctness import Params, PARAMS
import numpy as np
from user_action import (
    UserAction,
    construct_user_swap_a_to_b,
    construct_user_swap_b_to_a,
)
from pool.pool import Pool
from prices_snapshot import PricesSnapshot
from pool.pool import Pool
from common import capital_function
from user.informed_user import InformedUser


def find_optimal_action_by_bruteforce(
    pool: Pool,
    network_fee: float,
    prices: PricesSnapshot,
):
    N_SAMPLES = 100

    possible_actions: list[tuple[UserAction, float]] = []

    def _process_action(action: UserAction):
        user_balance_change = action.get_user_balance_change()
        markout = capital_function(
            user_balance_change.delta_x, user_balance_change.delta_y, prices
        )
        print(f"Action: {action}")
        possible_actions.append((action, markout))

    for amount_to_exchange_A in np.linspace(
        0, pool.liquidity_state.quantity_a, N_SAMPLES
    ):
        action = construct_user_swap_a_to_b(
            pool.liquidity_state,
            pool.fee_algorithm.get_a_to_b_exchange_fee_rate(pool.liquidity_state),
            amount_to_exchange_A,
        )
        _process_action(action)

    for amount_to_exchange_B in np.linspace(
        0, pool.liquidity_state.quantity_b, N_SAMPLES
    ):
        action = construct_user_swap_b_to_a(
            pool.liquidity_state,
            pool.fee_algorithm.get_b_to_a_exchange_fee_rate(pool.liquidity_state),
            amount_to_exchange_B,
        )
        _process_action(action)

    return max(possible_actions, key=lambda x: x[1])[0]


@pytest.mark.parametrize("test_params", PARAMS)
def test_informed_user_optimal_action(test_params: Params):
    theoretical_action = InformedUser().get_user_action(
        pool=test_params.pool,
        network_fee=test_params.network_fee,
        prices=test_params.prices,
    )
    print(f"Theoretical action: {theoretical_action}")

    bruteforce_action = find_optimal_action_by_bruteforce(
        pool=test_params.pool,
        network_fee=test_params.network_fee,
        prices=test_params.prices,
    )

    print(f"Bruteforce action: {bruteforce_action}")

    theoretical_action_markout = 0
    if theoretical_action is not None:
        theoretical_action_markout = capital_function(
            theoretical_action.get_user_balance_change().delta_x,
            theoretical_action.get_user_balance_change().delta_y,
            test_params.prices,
        )

    bruteforce_action_markout = 0
    if bruteforce_action is not None:
        bruteforce_action_markout = capital_function(
            bruteforce_action.get_user_balance_change().delta_x,
            bruteforce_action.get_user_balance_change().delta_y,
            test_params.prices,
        )

    assert theoretical_action_markout >= bruteforce_action_markout
