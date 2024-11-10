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


class UserType(Enum):
    INFORMED = enum.auto()
    UNINFORMED = enum.auto()


@dataclasses.dataclass
class ParticipantState:
    total_profit: float = 0

    def process_trade(
        self,
        delta_x: float,
        delta_y: float,
        fair_price_A: float,
        fair_price_B: float,
    ):
        deal_profit = capital_function(delta_x, delta_y, fair_price_A, fair_price_B)
        self.total_profit += deal_profit


@dataclasses.dataclass
class SimulationState:
    user_states: dict[UserType, ParticipantState]
    profits_LP: ParticipantState


@dataclasses.dataclass
class SimulationResult:
    snapshots: list[SimulationState] = dataclasses.field(default_factory=list)
    timestamps: list[pd.Timestamp] = dataclasses.field(default_factory=list)


class Simulation:
    def __init__(
        self,
        initial_quantity_A: float,
        initial_quantity_B: float,
        network_fee: float,
        alpha: float,
    ):
        """
        Args:
        initial_quantity_A: float, the initial number of shares of asset A in the pool
        initial_quantity_B: float, the initial number of shares of asset B in the pool
        network_fee: float, the network fee
        alpha: float, the fee rate
        """

        self.quantity_A = initial_quantity_A
        self.quantity_B = initial_quantity_B
        self.network_fee = network_fee
        self.alpha = alpha

        self.current_state = SimulationState(
            user_states={
                UserType.INFORMED: ParticipantState(),
                UserType.UNINFORMED: ParticipantState(),
            },
            profits_LP=ParticipantState(),
        )

    def simulate(
        self,
        p_IU: float,
        p_UU: float,
        informed_user: InformedUser,
        uninformed_user: UninformedUser,
        prices: pd.DataFrame,
    ) -> SimulationResult:
        """
        Simulate the trading process.

        Probabilities of deals on each step is simulated with fixed probabilities p_IU and p_UU

        Args:
        p_IU: float, the probability of the informed user to make a deal
        p_UU: float, the probability of the uninformed user to make a deal
        informed_user: InformedUser, the informed user
        uninformed_user: UninformedUser, the uninformed user
        prices: pd.DataFrame, the prices of the assets
            Column "price_A" contains "fair" prices of asset A
            Column "price_B" contains "fair" prices of asset B
            Column "time" contains the time moments
        """
        result = SimulationResult()

        for _, row in prices.iterrows():
            self.current_state = deepcopy(self.current_state)

            fair_price_A = row["price_A"]
            fair_price_B = row["price_B"]

            if self._trade(p_UU):
                self.process_deal(
                    UserType.UNINFORMED,
                    uninformed_user,
                    self.quantity_A,
                    self.quantity_B,
                    fair_price_A,
                    fair_price_B,
                )

            if self._trade(p_IU):
                self.process_deal(
                    UserType.INFORMED,
                    informed_user,
                    self.quantity_A,
                    self.quantity_B,
                    fair_price_A,
                    fair_price_B,
                )

            result.snapshots.append(self.current_state)
            result.timestamps.append(row["time"])

        return result

    def process_deal(
        self,
        user_type: UserType,
        user: User,
        token1_quantity: float,
        token2_quantity: float,
        fair_price_A: float,
        fair_price_B: float,
    ):
        """
        Process the deal
        """
        logging.info(
            f"Processing deal for {user_type}, current pool state: {self.quantity_A}, {self.quantity_B}, current fair prices: {fair_price_A}, {fair_price_B}"
        )
        user_action = user.get_user_action(
            token1_quantity,
            token2_quantity,
            self.alpha,
            self.network_fee,
            fair_price_A,
            fair_price_B,
        )
        logging.info(f"User action: {user_action}")
        if user_action is None:
            return

        # Signs of delta_x and delta_y are relative to the user
        self.quantity_A -= user_action.delta_x
        self.quantity_B -= user_action.delta_y

        self.current_state.user_states[user_type].process_trade(
            user_action.delta_x, user_action.delta_y, fair_price_A, fair_price_B
        )

        self.current_state.profits_LP.process_trade(
            -user_action.delta_x, -user_action.delta_y, fair_price_A, fair_price_B
        )

        logging.info(
            f"Pool state after the deal: {self.quantity_A}, {self.quantity_B}, current fair prices: {fair_price_A}, {fair_price_B}"
        )

    def _trade(self, probability: float):
        return np.random.rand() < probability
