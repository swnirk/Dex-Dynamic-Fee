import pytest

from common import capital_function
from user.informed_user import InformedUser
from user.informed_user_bruteforce import InformedUserBruteforce
from tests.pool_snapshot import PoolSnapshot, POOL_SNAPSHOTS_TO_TEST


@pytest.mark.parametrize("test_params", POOL_SNAPSHOTS_TO_TEST)
def test_informed_user_optimal_action(test_params: PoolSnapshot):
    theoretical_action = InformedUser().get_user_action(
        pool=test_params.pool,
        network_fee=test_params.network_fee,
        prices=test_params.prices,
    )
    print(f"Theoretical action: {theoretical_action}")

    bruteforce_action = InformedUserBruteforce(n_samples=10000).get_user_action(
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
