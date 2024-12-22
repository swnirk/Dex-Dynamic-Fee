from experiments.data import get_experiment_data
from experiments.experiment import Experiment
from pathlib import Path
from visualizations.utility import get_initial_pool_sizes
from pool.pool import Pool
from pool.liquidity_state import PoolLiquidityState
from simulation.simulation import Simulation
from experiments.experiment import ExperimentResult

DATA_ROOT = Path("data")


def run_experiment(
    experiment: Experiment, data_root: Path = DATA_ROOT
) -> ExperimentResult:
    experiment_data = get_experiment_data(data_root, experiment.data)

    initial_quantity_A, initial_quantity_B = get_initial_pool_sizes(
        # experiment_data["price_A"].iloc[0], experiment_data["price_B"].iloc[0], 100000
        experiment_data["price_A"].iloc[0], experiment_data["price_B"].iloc[0], 26263564.075505912 # in USDT
    )

    pool = Pool(
        liquidity_state=PoolLiquidityState(
            quantity_a=initial_quantity_A, quantity_b=initial_quantity_B
        ),
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
