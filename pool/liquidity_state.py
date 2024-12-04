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
