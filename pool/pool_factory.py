from pool.simple_pool import SimplePool
from pool.dynamic_fee_pool import DynamicFeeNumDeals, DynamicFeeVolDeals
from pool.abstract_pool import Pool, PoolLiquidityState

class PoolFactory:
    POOL_CLASSES = {
        "SimpleFee": SimplePool,
        "DynamicFeeNumDeals": DynamicFeeNumDeals,
        "DynamicFeeVolDeals": DynamicFeeVolDeals
    }

    @staticmethod
    def create_pool(liquidity_state: PoolLiquidityState, Fee_algo: str, **kwargs) -> Pool:
        PoolClass = PoolFactory.POOL_CLASSES.get(Fee_algo)
        if not PoolClass:
            raise ValueError(f"Unknown fee algorithm: {Fee_algo}")
        return PoolClass(liquidity_state=liquidity_state, **kwargs)
