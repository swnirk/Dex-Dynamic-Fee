import numpy as np

def dynamic_fee(delta, reserve, f_min=0.001, f_max=0.005, z0=0.01):
        ratio = abs(delta) / reserve
        fee_rate = f_min + (f_max - f_min) / (1 + np.exp(-(ratio - z0)))
        return fee_rate
    
def arbitrage_profit_A_to_B(x, y, delta, pCEX):
    fee = dynamic_fee(delta, x)
    effective_delta = delta * (1 - fee)
    delta_y = y - (x * y) / (x + effective_delta)
    profit = pCEX * delta_y - delta
    return profit