from dataclasses import dataclass
from common import get_amm_exchange_value_a_to_b
from pool.pool import PoolLiquidityState
import logging
from balance_change import BalanceChange
from fee_algorithm.base import FeeAlgorithm
from common import capital_function
from prices_snapshot import PricesSnapshot
from math import isclose


@dataclass
class UserAction:
    #  delta_x and delta_y are "user-side"
    delta_x: float
    delta_y: float

    # fee_x and fee_y are "user-side" -- fee paid by user (thus, always non-negative)
    fee_x: float
    fee_y: float

    network_fee: float

    # For example, if user want to change X -> Y, then:
    # - delta_x < 0
    # - delta_y > 0
    # - fee_x >= 0
    # - fee_y = 0

    # If user performs action, then:
    # - user balance changes as follows: x += delta_x, y += delta_y
    # - only the non-fee part participates in the swap invariant
    # - but the full input amount, including the fee, is deposited into the pool
    # - final pool balance changes as follows: x -= delta_x, y -= delta_y

    def get_user_balance_change(self) -> BalanceChange:
        return BalanceChange(self.delta_x, self.delta_y)

    def get_invariant_pool_balance_change(self) -> BalanceChange:
        # This is the balance change during the swap-stage, where only the
        # input amount net of fees is allowed to affect the invariant.
        return BalanceChange(-self.delta_x - self.fee_x, -self.delta_y - self.fee_y)

    def get_pool_balance_change(self) -> BalanceChange:
        return BalanceChange(-self.delta_x, -self.delta_y)

    def get_lp_balance_change(self) -> BalanceChange:
        # LP owns the pool reserves, including the fee returned to the pool.
        return self.get_pool_balance_change()

    def get_lp_markout(self, prices: PricesSnapshot) -> float:
        lp_balance_change = self.get_lp_balance_change()
        return capital_function(
            lp_balance_change.delta_x, lp_balance_change.delta_y, prices
        )

    def get_user_markout(self, prices: PricesSnapshot) -> float:
        user_balance_change = self.get_user_balance_change()
        return (
            capital_function(
                user_balance_change.delta_x, user_balance_change.delta_y, prices
            )
            - self.network_fee
        )

    def get_turnover(self, prices: PricesSnapshot):
        if self.delta_x > 0:
            return self.delta_x * prices.price_a
        else:
            return self.delta_y * prices.price_b

    def inverse(self) -> "UserAction":
        return UserAction(
            self.delta_y, self.delta_x, self.fee_y, self.fee_x, self.network_fee
        )


def construct_user_swap_a_to_b(
    pool_state: PoolLiquidityState,
    fee_algo: FeeAlgorithm,
    *,
    amount_to_exchange_A: float,
    network_fee: float,
) -> UserAction:
    """
    Returns formed UserAction struct based amount_to_exchange of token A

    Args:
    amount_to_exchange_A: float, the amount of token A user sends to the pool (before any fee deduction)
    network_fee: float, the network fee user pays for the transaction
    """
    assert amount_to_exchange_A >= 0

    fee_paid_in_A = fee_algo.get_a_to_b_trade_fee(pool_state, amount_to_exchange_A)
    amount_to_exchange_A_after_fee = amount_to_exchange_A - fee_paid_in_A

    if amount_to_exchange_A_after_fee < 0 and isclose(
        amount_to_exchange_A_after_fee, 0.0, abs_tol=1e-12
    ):
        amount_to_exchange_A_after_fee = 0.0

    assert amount_to_exchange_A_after_fee >= 0, (
        "Swap input after fee is negative: "
        f"amount_to_exchange_A={amount_to_exchange_A}, "
        f"fee_paid_in_A={fee_paid_in_A}, "
        f"amount_to_exchange_A_after_fee={amount_to_exchange_A_after_fee}, "
        f"fee_algo={type(fee_algo).__name__}"
    )

    pool_change_b = get_amm_exchange_value_a_to_b(
        pool_state.quantity_a, pool_state.quantity_b, amount_to_exchange_A_after_fee
    )

    if pool_change_b > 0 and isclose(pool_change_b, 0.0, abs_tol=1e-12):
        pool_change_b = 0.0

    assert pool_change_b <= 0, (
        "AMM output must be non-positive from the pool perspective: "
        f"quantity_a={pool_state.quantity_a}, "
        f"quantity_b={pool_state.quantity_b}, "
        f"amount_to_exchange_A_after_fee={amount_to_exchange_A_after_fee}, "
        f"pool_change_b={pool_change_b}"
    )

    return UserAction(
        -amount_to_exchange_A, -pool_change_b, fee_paid_in_A, 0, network_fee
    )


def construct_user_swap_b_to_a(
    pool_state: PoolLiquidityState,
    fee_algo: FeeAlgorithm,
    *,
    amount_to_exchange_B: float,
    network_fee: float,
) -> UserAction:
    """
    See construct_user_swap_a_to_b
    """
    action = construct_user_swap_a_to_b(
        pool_state.inverse(),
        fee_algo.inverse(),
        amount_to_exchange_A=amount_to_exchange_B,
        network_fee=network_fee,
    )
    return action.inverse()


def validate_user_action(
    pool_state: PoolLiquidityState,
    action: UserAction,
) -> None:
    logging.debug(
        f"Validating user action num A: {pool_state.quantity_a}, delta_x: {action.delta_x}, num B: {pool_state.quantity_b}, delta_y: {action.delta_y}"
    )
    pool_balance_change = action.get_pool_balance_change()
    assert pool_state.quantity_a + pool_balance_change.delta_x >= 0
    assert pool_state.quantity_b + pool_balance_change.delta_y >= 0
    assert action.delta_x * action.delta_y <= 0
    if action.delta_x <= 0:
        assert action.fee_x >= 0
    if action.delta_y <= 0:
        assert action.fee_y >= 0
