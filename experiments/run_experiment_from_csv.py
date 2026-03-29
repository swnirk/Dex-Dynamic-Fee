"""
Run a single experiment from a pre-downloaded CSV file.

Used by fee_algorithms_comparison_new_pairs.ipynb so that experiments
can be dispatched to ProcessPoolExecutor (pickling requires the worker
function to live in a proper module, not in __main__).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from experiments.experiment import Experiment, ExperimentResult
from pool.liquidity_state import PoolLiquidityState
from pool.pool import Pool
from simulation.simulation import Simulation


def run_experiment_from_csv(
    csv_path: str,
    experiment: Experiment,
    return_intermediate_results: bool = True,
    max_rows: Optional[int] = None,
    snapshot_every_n: int = 720,
) -> ExperimentResult:
    """
    snapshot_every_n: keep only every N-th intermediate snapshot to limit memory
        usage while still allowing time-series plots.
        Default 720 means one point per ~2.4 h for 12 s candles.
        Set to 1 to keep every snapshot (high memory).
    """
    np.random.seed(experiment.random_seed)

    data_df = pd.read_csv(csv_path)
    data_df["time"] = pd.to_datetime(data_df["time"])
    if max_rows is not None:
        data_df = data_df.iloc[:max_rows]

    initial_pool_state = PoolLiquidityState(
        quantity_a=experiment.initial_pool_value / 2 / data_df["price_A"].iloc[0],
        quantity_b=experiment.initial_pool_value / 2 / data_df["price_B"].iloc[0],
    )
    pool = Pool(
        liquidity_state=initial_pool_state,
        fee_algorithm=experiment.fee_algorithm,
    )
    simulation = Simulation(
        pool=pool,
        network_fee=experiment.network_fee,
        lp_metrics_price_source=experiment.lp_metrics_price_source,
    )
    simulation_result = simulation.simulate(
        p_UU=experiment.uninformed_users.probability_of_trade,
        num_UU=experiment.uninformed_users.n_users,
        uninformed_user=experiment.uninformed_users.uninformed_user,
        informed_user=experiment.informed_user,
        prices=data_df,
        return_intermediate_results=return_intermediate_results,
    )

    # Subsample snapshots to reduce memory: keep every N-th + always the last.
    if return_intermediate_results and snapshot_every_n > 1:
        snaps = simulation_result.snapshots
        times = simulation_result.timestamps
        indices = list(range(0, len(snaps), snapshot_every_n))
        if indices[-1] != len(snaps) - 1:
            indices.append(len(snaps) - 1)
        simulation_result.snapshots = [snaps[i] for i in indices]
        simulation_result.timestamps = [times[i] for i in indices]

    return ExperimentResult(
        data=data_df,
        experiment=experiment,
        pool=pool,
        simulation_result=simulation_result,
    )
