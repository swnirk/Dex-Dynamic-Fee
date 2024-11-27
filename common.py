from prices_snapshot import PricesSnapshot


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
    quantity_A: float, quantity_B: float, delta_A: float, fee_rate: float, AMM_type: str,
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
    if AMM_type == "constant_product":
        return (quantity_A * quantity_B) / (quantity_A + delta_A) - quantity_B
    elif AMM_type == "constant_sum":
        return -delta_A*(1 - fee_rate)
