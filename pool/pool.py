from dataclasses import dataclass
from balance_change import BalanceChange
from pool.liquidity_state import PoolLiquidityState
from fee_algorithm.base import FeeAlgorithm


@dataclass
class Pool:
    liquidity_state: PoolLiquidityState
    fee_algorithm: FeeAlgorithm

    def inverse_pool(self) -> "Pool":
        return Pool(self.liquidity_state.inverse(), self.fee_algorithm.inverse())

    def get_a_to_b_exchange_fee_rate(self) -> float:
        return self.fee_algorithm.get_a_to_b_exchange_fee_rate(self.liquidity_state)

    def get_b_to_a_exchange_fee_rate(self) -> float:
        return self.fee_algorithm.get_b_to_a_exchange_fee_rate(self.liquidity_state)

    def process_oracle_price(self, a_to_b_price: float):
        self.fee_algorithm.process_oracle_price(a_to_b_price)

    def process_trade(self, balance_change: BalanceChange):
        self.liquidity_state.process_trade(balance_change)
        self.fee_algorithm.process_trade(balance_change)

    def get_a_to_b_exchange_price(self) -> float:
        return self.liquidity_state.quantity_b / self.liquidity_state.quantity_a
