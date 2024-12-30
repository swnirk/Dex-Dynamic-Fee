from experiments.experiment import GBMParameters
from experiments.experiment import SyntheticDataDescription
import numpy as np
import pandas as pd


def extract_gbm_params(time_series: np.ndarray, delta_t: float = 1) -> GBMParameters:
    """
    Extracts GBM parameters from a time series of prices.

    Args:
        time_series: A 2D NumPy array where rows are assets and columns are prices over time.
        delta_t: Time step between consecutive observations (default is 1).

    Returns:
        A GBMParameters dataclass containing S0, mu, and cov_matrix.
    """
    # Calculate log returns
    log_returns = np.log(time_series[:, 1:] / time_series[:, :-1])

    # Extract initial prices
    S0 = time_series[:, 0].tolist()

    # Calculate drift (mu) and covariance matrix
    mu = (log_returns.mean(axis=1) / delta_t).tolist()
    cov_matrix = np.cov(log_returns, rowvar=True)

    return GBMParameters(S0=S0, mu=mu, cov_matrix=cov_matrix)


def gbm(params: GBMParameters, T: float, steps: int) -> np.ndarray:
    """
    Simulates paths of a Geometric Brownian Motion (GBM) for multiple assets.

    Args:
        params: An instance of GBMParameters containing S0, mu, and cov_matrix.
        T: Total time for simulation.
        steps: Number of time steps.

    Returns:
        paths: Simulated paths (2D array of shape n x (steps + 1)).
    """
    S0 = np.array(params.S0)
    mu = np.array(params.mu)
    cov_matrix = params.cov_matrix

    n = len(S0)
    dt = T / steps

    # Initialize paths
    paths = np.zeros((n, steps + 1))
    paths[:, 0] = S0

    # Calculate volatilities (sigma)
    sigma = np.sqrt(np.diagonal(cov_matrix))

    # Simulate paths
    for t in range(1, steps + 1):
        # Generate correlated random variables
        correlated_Z = np.random.multivariate_normal(mean=np.zeros(n), cov=cov_matrix)

        # Update paths using GBM formula
        paths[:, t] = paths[:, t - 1] * np.exp(
            (mu - 0.5 * sigma**2) * dt + np.sqrt(dt) * correlated_Z
        )

    return paths


def generate_synthetic_data(description: SyntheticDataDescription) -> pd.DataFrame:
    """
    Generates synthetic data based on the provided description.

    Args:
        description: An instance of SyntheticDataDescription.

    Returns:
        data: A DataFrame containing synthetic data.
    """

    time_series = list(
        pd.date_range(
            start=description.start_time,
            end=description.end_time,
            freq=description.candle_interval,
        )
    )

    paths = gbm(
        params=description.gbm_parameters,
        T=len(time_series) - 1,
        steps=len(time_series) - 1,
    )

    return pd.DataFrame(
        {
            "time": time_series,
            "price_A": paths[0],
            "price_B": paths[1],
        }
    )
