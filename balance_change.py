from dataclasses import dataclass


@dataclass
class BalanceChange:
    delta_x: float
    delta_y: float

    def inverse(self) -> "BalanceChange":
        return BalanceChange(-self.delta_x, -self.delta_y)
