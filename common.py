def capital_function(
    position_A: float, position_B: float, price_A: float, price_B: float
) -> float:
    """
    Calculate the total value of the portfolio
    Args:
    position_A: float, the number of shares of asset A
    position_B: float, the number of shares of asset B
    price_A: float, the price of asset A
    price_B: float, the price of asset B

    Returns:
    float: the total value of the portfolio
    """
    return position_A * price_A + position_B * price_B


def get_amm_exchange_value_a_to_b(
    quantity_A: float, quantity_B: float, delta_A: float
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
    return (quantity_A * quantity_B) / (quantity_A + delta_A) - quantity_B
