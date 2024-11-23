from dataclasses import dataclass
from pool.abstract_pool import Pool, PoolLiquidityState
import logging


@dataclass
class DynamicFeePool(Pool):
    liquidity_state: PoolLiquidityState

    alpha: float  # fee rate
    gamma: float

    num_A_to_B_deals: int = 0
    num_B_to_A_deals: int = 0

    def inverse_pool(self) -> "DynamicFeePool":
        return DynamicFeePool(self.liquidity_state.inverse(), self.gamma, self.alpha)

    def get_a_to_b_exchange_fee_rate(self) -> float:
        return self.alpha
    
    def get_b_to_a_exchange_fee_rate(self) -> float:
        return self.gamma

    def process_trade(self, delta_a: float, delta_b: float):

        self.liquidity_state.process_trade(delta_a, delta_b)

        if delta_a < 0:
            self.num_A_to_B_deals += 1
        elif delta_b < 0:
            self.num_B_to_A_deals += 1

        delta = self.num_A_to_B_deals - self.num_B_to_A_deals
        if abs(delta) > 5:
            if delta > 0 and self.alpha < 0.03:
                self.alpha += 0.001
            elif delta < 0 and self.gamma < 0.03:
                self.gamma += 0.001

        logging.info(
            f"Updated fees: alpha={self.alpha}, gamma={self.gamma}, "
            f"num_A_to_B_deals={self.num_A_to_B_deals}, num_B_to_A_deals={self.num_B_to_A_deals}"
        )
