import numpy as np
from user.abstract_user import (
    User,
    UserAction,
    construct_user_swap_a_to_b,
    validate_user_action,
)
from typing import Optional
from common import get_dex_a_to_b_price
import logging


class InformedUser(User):
    def get_user_action(
        self,
        token1_quantity: float,
        token2_quantity: float,
        alpha: float,
        network_fee: float,
        fair_price_A: float,
        fair_price_B: float,
    ) -> Optional[UserAction]:
        # Notation to match the paper
        x = token1_quantity
        y = token2_quantity
        q = fair_price_A / fair_price_B

        action: Optional[UserAction] = None

        if get_dex_a_to_b_price(x, y) > q:
            logging.debug("Users swaps A -> B")
            action = self._get_optimal_a_to_b_swap(
                token1_quantity,
                token2_quantity,
                alpha,
                network_fee,
                fair_price_A,
                fair_price_B,
            )

        elif get_dex_a_to_b_price(x, y) < q:
            logging.debug("Users swaps B -> A")
            action = self._get_optimal_a_to_b_swap(
                token2_quantity,
                token1_quantity,
                alpha,
                network_fee,
                fair_price_B,
                fair_price_A,
            )
            action = UserAction(action.delta_y, action.delta_x, action.fee)
        else:
            return None

        logging.debug(f"User action: {action}")

        validate_user_action(token1_quantity, token2_quantity, action)

        return action

    def _get_optimal_a_to_b_swap(
        self,
        token1_quantity: float,
        token2_quantity: float,
        alpha: float,
        network_fee: float,
        fair_price_A: float,
        fair_price_B: float,
    ) -> UserAction:
        x = token1_quantity
        y = token2_quantity
        q = fair_price_A / fair_price_B
        beta = 1 - alpha

        assert get_dex_a_to_b_price(x, y) > q

        # In terms of "pool" balance;
        # So, if optimal_delta_x is 1, than optimal action is increasing pool's x-balance by 1 and thus selling 1 unit of x
        optimal_delta_x = (np.sqrt(x * y / q) - x) / beta

        assert optimal_delta_x >= 0

        logging.debug(f"Optimal delta x: {optimal_delta_x}")

        action = construct_user_swap_a_to_b(
            x, y, alpha, fair_price_A, fair_price_B, optimal_delta_x
        )

        return action
