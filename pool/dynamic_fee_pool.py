from dataclasses import dataclass
from pool.abstract_pool import Pool, PoolLiquidityState
import logging
from balance_change import BalanceChange


@dataclass
class DynamicFeeNumDeals(Pool):
    liquidity_state: PoolLiquidityState

    AMM_algo: str

    alpha: float  # fee rate
    gamma: float

    fee_step: float = 0.0001

    num_A_to_B_deals: int = 0
    num_B_to_A_deals: int = 0

    def inverse_pool(self) -> "DynamicFeeNumDeals":
        return DynamicFeeNumDeals(self.liquidity_state.inverse(), self.AMM_algo, self.gamma, self.alpha, self.fee_step)

    def get_a_to_b_exchange_fee_rate(self) -> float:
        return self.alpha

    def get_b_to_a_exchange_fee_rate(self) -> float:
        return self.gamma

    def process_trade(self, balance_change: BalanceChange):

        self.liquidity_state.process_trade(balance_change)

        delta_a = balance_change.delta_x
        delta_b = balance_change.delta_y

        if delta_a < 0:
            self.num_A_to_B_deals += 1
        elif delta_b < 0:
            self.num_B_to_A_deals += 1

        delta = self.num_A_to_B_deals - self.num_B_to_A_deals
        if abs(delta) > 5:
            if delta > 0 and self.gamma >= self.fee_step and self.alpha <= 0.003:
                self.alpha += self.fee_step
                self.gamma -= self.fee_step
            elif delta < 0 and self.alpha >= self.fee_step and self.gamma <=0.003:
                self.gamma += self.fee_step
                self.alpha -= self.fee_step

        logging.info(
            f"Updated fees: alpha={self.alpha}, gamma={self.gamma}, "
            f"num_A_to_B_deals={self.num_A_to_B_deals}, num_B_to_A_deals={self.num_B_to_A_deals}"
        )


@dataclass
class DynamicFeeVolDeals(Pool):
    liquidity_state: PoolLiquidityState

    alpha: float  # fee rate
    gamma: float

    fee_step: float = 0.0001

    vol_A_to_B_deals: float = 0.0
    vol_B_to_A_deals: float = 0.0

    def inverse_pool(self) -> "DynamicFeeVolDeals":
        return DynamicFeeVolDeals(self.liquidity_state.inverse(), self.gamma, self.alpha)

    def get_a_to_b_exchange_fee_rate(self) -> float:
        return self.alpha

    def get_b_to_a_exchange_fee_rate(self) -> float:
        return self.gamma

    def process_trade(self, balance_change: BalanceChange):

        self.liquidity_state.process_trade(balance_change)

        delta_a = balance_change.delta_x
        delta_b = balance_change.delta_y

        if delta_a < 0:
            self.vol_A_to_B_deals += -delta_a
        elif delta_b < 0:
            self.vol_B_to_A_deals += -delta_b
        
        # TODO: logic for fee update

        # delta = self.vol_A_to_B_deals - self.vol_B_to_A_deals
        # if abs(delta) > 5:
        #     if delta > 0 and self.gamma >= self.fee_step:
        #         self.alpha += self.fee_step
        #         self.gamma -= self.fee_step
        #     elif delta < 0 and self.alpha >= self.fee_step:
        #         self.gamma += self.fee_step
        #         self.alpha -= self.fee_step

        logging.info(
            f"Updated fees: alpha={self.alpha}, gamma={self.gamma}, "
            f"num_A_to_B_deals={self.num_A_to_B_deals}, num_B_to_A_deals={self.num_B_to_A_deals}"
        )

