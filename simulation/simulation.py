import dataclasses
from user.abstract_user import User
from user.informed_user import InformedUser
from user.uninformed_user import UninformedUser
import numpy as np
import pandas as pd
import dataclasses
from common import capital_function
from enum import Enum
import enum
import logging
from copy import deepcopy
from pool.abstract_pool import Pool
from prices_snapshot import PricesSnapshot
import dataclasses


class UserType(Enum):
    INFORMED = enum.auto()
    UNINFORMED = enum.auto()


@dataclasses.dataclass
class Position:
    position_a: float
    position_b: float

    def process_trade(self, delta_x: float, delta_y: float):
        self.position_a += delta_x
        self.position_b += delta_y


@dataclasses.dataclass
class ParticipantState:
    total_markout: float = 0
    position: Position = dataclasses.field(
        default_factory=lambda: Position(position_a=0, position_b=0)
    )
    valuation: float = 0

    def update_valuation(self, prices: PricesSnapshot):
        self.valuation = capital_function(
            self.position.position_a, self.position.position_b, prices
        )

    def process_trade(
        self,
        delta_x: float,
        delta_y: float,
        prices: PricesSnapshot,
    ):
        deal_markout = capital_function(delta_x, delta_y, prices)
        self.total_markout += deal_markout
        self.position.process_trade(delta_x, delta_y)


@dataclasses.dataclass
class SimulationState:
    user_states: dict[UserType, ParticipantState]
    lp_state: ParticipantState
    lp_with_just_hold_strategy: ParticipantState


@dataclasses.dataclass
class SimulationResult:
    snapshots: list[SimulationState] = dataclasses.field(default_factory=list)
    timestamps: list[pd.Timestamp] = dataclasses.field(default_factory=list)


class Simulation:
    def __init__(
        self,
        pool: Pool,
        network_fee: float,
    ):
        """
        Args:
        pool: Pool, the pool
        network_fee: float, the network fee
        """

        self.pool = pool
        self.network_fee = network_fee
        self.num_A_to_B_deals = 0
        self.num_B_to_A_deals = 0

    def simulate(
        self,
        p_UU: float,
        informed_user: InformedUser,
        uninformed_user: UninformedUser,
        prices: pd.DataFrame,
    ) -> SimulationResult:
        """
        Simulate the trading process.

        Probabilities of UU deals on each step is simulated with probability p_UU

        Args:
        p_UU: float, the probability of the uninformed user to make a deal
        informed_user: InformedUser, the informed user
        uninformed_user: UninformedUser, the uninformed user
        prices: pd.DataFrame, the prices of the assets
            Column "price_A" contains "fair" prices of asset A
            Column "price_B" contains "fair" prices of asset B
            Column "time" contains the time moments
        """
        result = SimulationResult()

        initial_prices_snapshot = self._get_prices_snapshot(prices.iloc[0])

        # TODO: we suppose that we have only one LP -- this is very unrealistic assumption
        initial_lp_state = ParticipantState(
            total_markout=0,
            position=Position(
                position_a=self.pool.liquidity_state.quantity_a,
                position_b=self.pool.liquidity_state.quantity_b,
            ),
        )
        self.current_state = SimulationState(
            user_states={
                UserType.INFORMED: ParticipantState(),
                UserType.UNINFORMED: ParticipantState(),
            },
            lp_state=initial_lp_state,
            lp_with_just_hold_strategy=deepcopy(initial_lp_state),
        )

        self.current_state.lp_state.update_valuation(initial_prices_snapshot)

        for _, row in prices.iterrows():
            self.current_state = deepcopy(self.current_state)

            prices_snapshot = self._get_prices_snapshot(row)

            if self._trade(p_UU):
                self.process_deal(UserType.UNINFORMED, uninformed_user, prices_snapshot)

            self.process_deal(UserType.INFORMED, informed_user, prices_snapshot)

            self.current_state.lp_state.update_valuation(prices_snapshot)
            self.current_state.lp_with_just_hold_strategy.update_valuation(
                prices_snapshot
            )
            self.current_state.user_states[UserType.INFORMED].update_valuation(
                prices_snapshot
            )
            self.current_state.user_states[UserType.UNINFORMED].update_valuation(
                prices_snapshot
            )

            result.snapshots.append(self.current_state)
            result.timestamps.append(row["time"])

        return result

    def process_deal(
        self,
        user_type: UserType,
        user: User,
        prices: PricesSnapshot,
    ):
        """
        Process the deal
        """
        logging.info(
            f"Processing deal for {user_type}, current pool state: {self.pool.liquidity_state}, current fair prices: {prices}"
        )
        user_action = user.get_user_action(self.pool, self.network_fee, prices)

        logging.info(f"User action: {user_action}")
        if user_action is None:
            return

        if user_action.delta_x < 0:
            fee = self.pool.get_a_to_b_exchange_fee_rate()
            self.pool.process_trade(
                user_action.delta_x * (1 - fee), user_action.delta_y
            )
        elif user_action.delta_y < 0:
            fee = self.pool.get_b_to_a_exchange_fee_rate()
            self.pool.process_trade(
                user_action.delta_x, user_action.delta_y * (1 - fee)
            )

        self.current_state.user_states[user_type].process_trade(
            user_action.delta_x,
            user_action.delta_y,
            prices,
        )

        self.current_state.lp_state.process_trade(
            -user_action.delta_x, -user_action.delta_y, prices
        )

        logging.info(
            f"Pool state after the deal: {self.pool.liquidity_state}, current fair prices: {prices}"
        )

    def _trade(self, probability: float):
        return np.random.rand() < probability

    def _get_prices_snapshot(self, row: pd.Series):
        fair_price_A = row["price_A"]
        fair_price_B = row["price_B"]
        return PricesSnapshot(fair_price_A, fair_price_B)
