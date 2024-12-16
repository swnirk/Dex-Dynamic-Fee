import dataclasses
from pool.pool import Pool
from prices_snapshot import PricesSnapshot
from pool.pool import Pool, PoolLiquidityState
from fee_algorithm.fixed_fee import FixedFee
from fee_algorithm.fee_based_on_trade import FeeBasedOnTrade
from prices_snapshot import PricesSnapshot
import dataclasses


@dataclasses.dataclass
class PoolSnapshot:
    pool: Pool
    network_fee: float
    prices: PricesSnapshot

    def __post_init__(self) -> None:
        # Automatically prepare the pool when the object is initialized
        self.pool.process_oracle_price(self.prices.get_a_to_b_price())


_FEE_ALGORITHMS = [
    *[
        FixedFee(
            exchange_fee_rate=alpha,
        )
        for alpha in [0.01, 0.1, 0.9]
    ],
    *[
        FeeBasedOnTrade(
            default_fee_rate=alpha,
        )
        for alpha in [0.01, 0.1, 0.9]
    ],
]

POOL_SNAPSHOTS_TO_TEST = [
    PoolSnapshot(
        pool=Pool(
            liquidity_state=PoolLiquidityState(
                liquidity_a,
                liquidity_b,
            ),
            fee_algorithm=fee_algo,
        ),
        network_fee=network_fee,
        prices=prices,
    )
    for fee_algo in _FEE_ALGORITHMS
    for (liquidity_a, liquidity_b) in [
        (1, 1),
        (100, 100),
        (10000, 10000),
        (100, 1),
        (1, 100),
    ]
    for network_fee in [0, 0.1, 1000]
    for prices in [
        PricesSnapshot(2, 1),
        PricesSnapshot(1, 2),
        PricesSnapshot(1, 1),
        PricesSnapshot(100, 1),
        PricesSnapshot(1, 100),
    ]
]
