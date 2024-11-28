from prices_snapshot import PricesSnapshot
from pool.abstract_pool import Pool

def capital_function(
    position_A: float, position_B: float, prices: PricesSnapshot
) -> float:
    """
    Calculate the total value of the portfolio
    Args:
    position_A: float, the number of shares of asset A
    position_B: float, the number of shares of asset B
    prices: PricesSnapshot, the prices of tokens A and B

    Returns:
    float: the total value of the portfolio
    """
    return position_A * prices.price_a + position_B * prices.price_b


def get_amm_exchange_value_a_to_b(
    quantity_A: float, quantity_B: float, delta_A: float, pool: Pool
) -> float:
    """
    Calculate the value of the asset B that the AMM will return for the given amount of asset A
    Args:
    quantity_A: float, the amount of asset A in the pool
    quantity_B: float, the amount of asset B in the pool
    delta_A: float, the amount of asset A to exchange using the AMM

    Returns:
    float: the value of the asset B that the AMM will return
    """
    if pool.get_amm_type() == 'ConstProductAMM':
        return (quantity_A * quantity_B) / (quantity_A + delta_A) - quantity_B
    
    elif pool.get_amm_type() == 'ConstSumAMM':
        return -delta_A
    
    else:
        return "Unknown AMM type"
