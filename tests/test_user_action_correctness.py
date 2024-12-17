import pytest

from pool.pool import Pool, PoolLiquidityState
from fee_algorithm.continuous_fee_perfect_oracle import ContinuousFeePerfectOracle
from user.informed_user import InformedUser
from user.uninformed_user import UninformedUser
from user.abstract_user import UserAction
from user_action import validate_user_action
from prices_snapshot import PricesSnapshot
import dataclasses
from copy import deepcopy
import numpy as np
from tests.pool_snapshot import PoolSnapshot, POOL_SNAPSHOTS_TO_TEST
from user.abstract_user import User


@dataclasses.dataclass
class CorrectnessTestParams:
    pool_snapshot: PoolSnapshot
    user: User


PARAMS = [
    CorrectnessTestParams(
        pool_snapshot=pool_snapshot,
        user=user,
    )
    for user in [InformedUser(), UninformedUser()]
    for pool_snapshot in POOL_SNAPSHOTS_TO_TEST
]


def validate_constant_product_invariant_after_deal(
    pool_state: PoolLiquidityState, action: UserAction
):
    pool_state_after_deal = deepcopy(pool_state)

    pool_state_after_deal.process_trade(action.get_pool_balance_change())

    product_before = pool_state.quantity_a * pool_state.quantity_b
    product_after = pool_state_after_deal.quantity_a * pool_state_after_deal.quantity_b

    assert np.isclose(product_before, product_after)


@pytest.mark.parametrize("test_params", PARAMS)
def test_user_action_correctness(test_params: CorrectnessTestParams):
    action = InformedUser().get_user_action(
        pool=test_params.pool_snapshot.pool,
        network_fee=test_params.pool_snapshot.network_fee,
        prices=test_params.pool_snapshot.prices,
    )
    print(f"User action: {action}")

    if action is not None:
        validate_user_action(
            pool_state=test_params.pool_snapshot.pool.liquidity_state, action=action
        )
        validate_constant_product_invariant_after_deal(
            pool_state=test_params.pool_snapshot.pool.liquidity_state, action=action
        )
