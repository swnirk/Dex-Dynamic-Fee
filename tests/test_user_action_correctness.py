import pytest

from pool.abstract_pool import Pool, PoolLiquidityState
from pool.simple_pool import SimplePool
from user.informed_user import InformedUser
from user.uninformed_user import UninformedUser
from user.abstract_user import UserAction
from user_action import validate_user_action
from prices_snapshot import PricesSnapshot
import dataclasses
from copy import deepcopy
import numpy as np


@dataclasses.dataclass
class Params:
    pool: Pool
    network_fee: float
    prices: PricesSnapshot


PARAMS = [
    Params(
        pool=SimplePool(
            liquidity_state=PoolLiquidityState(
                liquidity_a,
                liquidity_b,
            ),
            alpha=alpha,
        ),
        network_fee=network_fee,
        prices=prices,
    )
    for (liquidity_a, liquidity_b) in [
        (1, 1),
        (100, 100),
        (10000, 10000),
        (100, 1),
        (1, 100),
    ]
    for alpha in [0.01, 0.1, 0.9]
    for network_fee in [0.01]
    for prices in [
        PricesSnapshot(2, 1),
        PricesSnapshot(1, 2),
        PricesSnapshot(1, 1),
        PricesSnapshot(100, 1),
        PricesSnapshot(1, 100),
    ]
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
def test_informed_user_action_correctness(test_params: Params):
    action = InformedUser().get_user_action(
        pool=test_params.pool,
        network_fee=test_params.network_fee,
        prices=test_params.prices,
    )
    print(f"User action: {action}")

    if action is not None:
        validate_user_action(pool_state=test_params.pool.liquidity_state, action=action)
        validate_constant_product_invariant_after_deal(
            pool_state=test_params.pool.liquidity_state, action=action
        )


@pytest.mark.parametrize("test_params", PARAMS)
def test_uninformed_user_action_correctness(test_params: Params):
    action = UninformedUser().get_user_action(
        pool=test_params.pool,
        network_fee=test_params.network_fee,
        prices=test_params.prices,
    )

    if action is not None:
        validate_user_action(pool_state=test_params.pool.liquidity_state, action=action)
