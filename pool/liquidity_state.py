from dataclasses import dataclass
from balance_change import BalanceChange


@dataclass
class PoolLiquidityState:
    quantity_a: float
    quantity_b: float

    def inverse(self) -> "PoolLiquidityState":
        return PoolLiquidityState(self.quantity_b, self.quantity_a)

    def process_trade(self, balance_change: BalanceChange):
        self.quantity_a += balance_change.delta_x
        self.quantity_b += balance_change.delta_y

    def get_a_to_b_exchange_price(self) -> float:
        return self.quantity_b / self.quantity_a

    def get_b_to_a_exchange_price(self) -> float:
        return self.quantity_a / self.quantity_b
