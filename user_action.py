from dataclasses import dataclass
from common import get_amm_exchange_value_a_to_b
from pool.pool import PoolLiquidityState
import logging
from balance_change import BalanceChange


@dataclass
class UserAction:
    #  delta_x and delta_y are "user-side"
    delta_x: float
    delta_y: float

    # fee_x and fee_y are "user-side" -- fee paid by user (thus, always non-negative)
    fee_x: float
    fee_y: float

    # For example, if user want to change X -> Y, then:
    # - delta_x < 0
    # - delta_y > 0
    # - fee_x >= 0
    # - fee_y = 0

    # If user performs action, then:
    # - user balance changes as follows: x += delta_x, y += delta_y
    # - liquidity reaches pool: (delta_x + fee_x, delta_y +fee_y)
    # - pool balance changes as follows: x -= (delta_x - fee_x), y -= (delta_y - fee_y)

    def get_user_balance_change(self) -> BalanceChange:
        return BalanceChange(self.delta_x, self.delta_y)

    def get_pool_balance_change(self) -> BalanceChange:
        return BalanceChange(-self.delta_x - self.fee_x, -self.delta_y - self.fee_y)

    def get_lp_balance_change(self) -> BalanceChange:
        # LP receives all the tokens paid by the user (including fees)
        return self.get_user_balance_change().inverse()

    def inverse(self) -> "UserAction":
        return UserAction(self.delta_y, self.delta_x, self.fee_y, self.fee_x)


def construct_user_swap_a_to_b(
    pool_state: PoolLiquidityState,
    fee_rate: float,
    amount_to_exchange_A: float,
) -> UserAction:
    """
    Returns formed UserAction struct based amount_to_exchange of token A

    Args:
    amount_to_exchange_A: float, the amount of token A user sends to the pool (before any fee deduction)
    """
    assert amount_to_exchange_A >= 0

    amount_to_exchange_A_after_fee = amount_to_exchange_A * (1 - fee_rate)
    fee_paid_in_A = amount_to_exchange_A * fee_rate

    assert amount_to_exchange_A_after_fee >= 0

    pool_change_b = get_amm_exchange_value_a_to_b(
        pool_state.quantity_a, pool_state.quantity_b, amount_to_exchange_A_after_fee
    )

    assert pool_change_b <= 0

    return UserAction(-amount_to_exchange_A, -pool_change_b, fee_paid_in_A, 0)


def construct_user_swap_b_to_a(
    pool_state: PoolLiquidityState,
    fee_rate: float,
    amount_to_exchange_B: float,
) -> UserAction:
    """
    See construct_user_swap_a_to_b
    """
    action = construct_user_swap_a_to_b(
        pool_state.inverse(),
        fee_rate,
        amount_to_exchange_B,
    )
    return action.inverse()


def validate_user_action(
    pool_state: PoolLiquidityState,
    action: UserAction,
) -> None:
    logging.debug(
        f"Validating user action num A: {pool_state.quantity_a}, delta_x: {action.delta_x}, num B: {pool_state.quantity_b}, delta_y: {action.delta_y}"
    )
    assert pool_state.quantity_a - (action.delta_x - action.fee_x) >= 0
    assert pool_state.quantity_b - (action.delta_y - action.fee_y) >= 0
    assert action.delta_x * action.delta_y <= 0
    if action.delta_x <= 0:
        assert action.fee_x >= 0
    if action.delta_y <= 0:
        assert action.fee_y >= 0
