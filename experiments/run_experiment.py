from experiments.data import get_experiment_data
from experiments.experiment import Experiment
from pathlib import Path
from pool.pool import Pool
from pool.liquidity_state import PoolLiquidityState
from simulation.simulation import Simulation
from experiments.experiment import ExperimentResult

DATA_ROOT = Path("data")


def get_initial_pool_state(
    price_A: float, price_B: float, total_pool_value_in_stablecoin: float
) -> PoolLiquidityState:
    """
    Returns the initial pool sizes for the two assets given the prices of the two assets

    Args:
        price_A (float): Price of asset A in terms of stablecoin
        price_B (float): Price of asset B in terms of stablecoin
        total_pool_value_in_stablecoin (float): Total value of the pool in terms of stablecoin
    """
    half_pool_value_in_stablecoin = total_pool_value_in_stablecoin / 2

    initial_quantity_A = half_pool_value_in_stablecoin / price_A
    initial_quantity_B = half_pool_value_in_stablecoin / price_B

    return PoolLiquidityState(
        quantity_a=initial_quantity_A, quantity_b=initial_quantity_B
    )


def run_experiment(
    experiment: Experiment, data_root: Path = DATA_ROOT
) -> ExperimentResult:
    experiment_data = get_experiment_data(data_root, experiment.data)

    initial_pool_state = get_initial_pool_state(
        experiment_data["price_A"].iloc[0],
        experiment_data["price_B"].iloc[0],
        total_pool_value_in_stablecoin=experiment.initial_pool_value,
    )

    pool = Pool(
        liquidity_state=initial_pool_state,
        fee_algorithm=experiment.fee_algorithm,
    )

    simulation = Simulation(
        pool=pool,
        network_fee=experiment.network_fee,
    )

    simulation_result = simulation.simulate(
        p_UU=experiment.uninformed_users.probability_of_trade,
        num_UU=experiment.uninformed_users.n_users,
        uninformed_user=experiment.uninformed_users.uninformed_user,
        informed_user=experiment.informed_user,
        prices=experiment_data,
    )

    return ExperimentResult(
        data=experiment_data,
        experiment=experiment,
        pool=pool,
        simulation_result=simulation_result,
    )
