import dataclasses
from user.abstract_user import User
import numpy as np
import pandas as pd
import dataclasses
from common import capital_function
from enum import Enum
import enum
import logging
from copy import deepcopy
from pool.pool import Pool
from prices_snapshot import PricesSnapshot
import dataclasses
from balance_change import BalanceChange
from user_action import validate_user_action


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
        balance_change: BalanceChange,
        deal_markout: float,
    ):
        self.total_markout += deal_markout
        self.position.process_trade(balance_change.delta_x, balance_change.delta_y)


@dataclasses.dataclass
class SimulationStateSnapshot:
    user_states: dict[UserType, ParticipantState]
    lp_state: ParticipantState
    lp_with_just_hold_strategy: ParticipantState
    prices: PricesSnapshot
    pool: Pool


@dataclasses.dataclass
class SimulationResult:
    snapshots: list[SimulationStateSnapshot] = dataclasses.field(default_factory=list)
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
        self.user_states = {
            UserType.INFORMED: ParticipantState(),
            UserType.UNINFORMED: ParticipantState(),
        }
        self.lp_state = ParticipantState()
        self.lp_with_just_hold_strategy = ParticipantState()

    def _get_current_state_snapshot(
        self, prices: PricesSnapshot
    ) -> SimulationStateSnapshot:
        return SimulationStateSnapshot(
            user_states=deepcopy(self.user_states),
            lp_state=deepcopy(self.lp_state),
            lp_with_just_hold_strategy=deepcopy(self.lp_with_just_hold_strategy),
            prices=deepcopy(prices),
            pool=deepcopy(self.pool),
        )

    def _update_all_valuations(self, prices: PricesSnapshot):
        for user_state in self.user_states.values():
            user_state.update_valuation(prices)
        self.lp_state.update_valuation(prices)
        self.lp_with_just_hold_strategy.update_valuation(prices)

    def simulate(
        self,
        p_UU: float,
        num_UU: int,
        informed_user: User,
        uninformed_user: User,
        prices: pd.DataFrame,
    ) -> SimulationResult:
        """
        Simulate the trading process.

        Probabilities of UU deals on each step is simulated with probability p_UU

        Args:
        p_UU: float, the probability of the uninformed user to make a deal
        num_UU: int, the number of uninformed users
        informed_user: InformedUser, the informed user
        uninformed_user: UninformedUser, the uninformed user
        prices: pd.DataFrame, the prices of the assets
            Column "price_A" contains "fair" prices of asset A
            Column "price_B" contains "fair" prices of asset B
            Column "time" contains the time moments
        """
        snapshots = []
        timestamps = []

        self.lp_state.position = Position(
            position_a=self.pool.liquidity_state.quantity_a,
            position_b=self.pool.liquidity_state.quantity_b,
        )

        self.lp_with_just_hold_strategy.position = deepcopy(self.lp_state.position)

        initial_prices_snapshot = self._get_prices_snapshot(prices.iloc[0])

        self._update_all_valuations(initial_prices_snapshot)

        self.pool.fee_algorithm.process_initial_pool_state(self.pool.liquidity_state)

        for _, row in prices.iterrows():
            prices_snapshot = self._get_prices_snapshot(row)

            self.pool.process_oracle_price(
                a_to_b_price=prices_snapshot.get_a_to_b_price()
            )

            for _ in range(num_UU):
                if self._trade(p_UU):
                    self.process_deal(
                        UserType.UNINFORMED, uninformed_user, prices_snapshot
                    )

            self.process_deal(UserType.INFORMED, informed_user, prices_snapshot)

            self._update_all_valuations(prices_snapshot)

            self.pool.fee_algorithm.process_block_end(self.pool.liquidity_state)

            snapshots.append(self._get_current_state_snapshot(prices_snapshot))
            timestamps.append(row["time"])

        return SimulationResult(snapshots=snapshots, timestamps=timestamps)

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

        validate_user_action(self.pool.liquidity_state, user_action)

        self.pool.process_trade(user_action.get_pool_balance_change())

        self.user_states[user_type].process_trade(
            user_action.get_user_balance_change(),
            user_action.get_user_markout(prices),
        )

        self.lp_state.process_trade(
            user_action.get_lp_balance_change(),
            user_action.get_lp_markout(prices),
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
