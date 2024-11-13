from dataclasses import dataclass
from abc import ABC, abstractmethod
from common import get_amm_exchange_value_a_to_b, capital_function
from typing import Optional
from pool.abstract_pool import PoolLiquidityState, Pool


@dataclass
class UserAction:
    # All fields are "user-side"
    # So, user balance will change as follows (x, y) -> (x + delta_x, y + delta_y)
    # And pool balance will change as follows (X, Y) -> (X - delta_x, Y - delta_y)
    delta_x: float
    delta_y: float
    fee: float


class User(ABC):
    @abstractmethod
    def get_user_action(
        self,
        pool: Pool,
        network_fee: float,
        fair_price_A: float,
        fair_price_B: float,
    ) -> Optional[UserAction]:
        """
        Args:
        pool: Pool, the pool
        network_fee: float, the network fee
        fair_price_A: float, the fair price of asset A
        fair_price_B: float, the fair price of asset B

        Returns:
        """
        pass


def construct_user_swap_a_to_b(
    pool_state: PoolLiquidityState,
    fee_rate: float,
    fair_price_A: float,
    fair_price_B: float,
    amount_to_exchange_A: float,
) -> UserAction:
    """
    Returns formed UserAction struct based amount_to_exchange of token A

    Args:
    amount_to_exchange_A: float, the amount of token A user wants to exchange
    """
    assert amount_to_exchange_A >= 0

    pool_change_b = get_amm_exchange_value_a_to_b(
        pool_state.quantity_a, pool_state.quantity_b, amount_to_exchange_A
    )

    assert pool_change_b <= 0

    fee = capital_function(
        amount_to_exchange_A * fee_rate,
        0,
        fair_price_A,
        fair_price_B,
    )
    return UserAction(-amount_to_exchange_A, -pool_change_b, fee)


def construct_user_swap_b_to_a(
    pool_state: PoolLiquidityState,
    fee_rate: float,
    fair_price_A: float,
    fair_price_B: float,
    amount_to_exchange_B: float,
) -> UserAction:
    """
    See construct_user_swap_a_to_b
    """
    action = construct_user_swap_a_to_b(
        pool_state.inverse(),
        fee_rate,
        fair_price_B,
        fair_price_A,
        amount_to_exchange_B,
    )
    return UserAction(action.delta_y, action.delta_x, action.fee)


def validate_user_action(
    pool_state: PoolLiquidityState,
    action: UserAction,
) -> None:
    assert pool_state.quantity_a - action.delta_x >= 0
    assert pool_state.quantity_b - action.delta_y >= 0
    assert action.delta_x * action.delta_y <= 0
