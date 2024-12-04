from dataclasses import dataclass


@dataclass
class PricesSnapshot:
    price_a: float
    price_b: float

    def inverse(self):
        return PricesSnapshot(self.price_b, self.price_a)

    def get_a_to_b_price(self):
        return self.price_a / self.price_b
