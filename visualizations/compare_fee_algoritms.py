import os
import seaborn as sns
import matplotlib.pyplot as plt
from simulation.simulation import UserType, SimulationResult
from experiments.experiment import Experiment, ExperimentResult
from experiments.run_multiple_experiments import (
    ExperimentDescriptionT,
    convert_experiment_key_to_dict,
)
import pandas as pd
from utility import fix_x_axis_labels


def extract_user_markouts(
    simulation_result: SimulationResult, user_type: UserType
) -> list:
    res = []
    for snapshot in simulation_result.snapshots:
        res.append(snapshot.user_states[user_type].total_markout)
    return res


def extract_lp_markouts(simulation_result: SimulationResult) -> list:
    res = []
    for snapshot in simulation_result.snapshots:
        res.append(snapshot.lp_state.total_markout)
    return res


def _plot_markouts_chart(
    markouts: dict[str, list[float]],
    timestamps: list[pd.Timestamp],
    user_type_name: str,
    period_alias: str,
):
    """
    Plot markouts chart

    markouts: dict[str, list[float]]
        keys -- descriptions (will be used as labels)
        values -- markouts
    """

    fig, ax = plt.subplots(figsize=(10, 6))

    for description, single_case_markouts in markouts.items():
        sns.lineplot(x=timestamps, y=single_case_markouts, ax=ax, label=description)

    fix_x_axis_labels(ax)

    plt.xlabel("Time")
    plt.ylabel("Markout")

    plt.xticks(rotation=45)
    plt.title(f"{user_type_name} markouts over time, {period_alias}")
    plt.tight_layout()

    plt.show()


def plot_participants_markouts(
    period_alias: str,
    results: dict[str, ExperimentResult],
):
    """
    results: dict[str, ExperimentResult]
        keys -- experiment names
        values -- ExperimentResult
    """
    timestamps = list(results.values())[0].simulation_result.timestamps

    # We don't need to plot uninformed users markouts charts as they are almost always trivial

    _plot_markouts_chart(
        markouts={
            f"{experiment_name}": extract_user_markouts(
                experiment_result.simulation_result, UserType.INFORMED
            )
            for experiment_name, experiment_result in results.items()
        },
        timestamps=timestamps,
        user_type_name="IU",
        period_alias=period_alias,
    )

    _plot_markouts_chart(
        markouts={
            f"{experiment_name}": extract_lp_markouts(
                experiment_result.simulation_result
            )
            for experiment_name, experiment_result in results.items()
        },
        timestamps=timestamps,
        user_type_name="LP",
        period_alias=period_alias,
    )


def extract_impermanent_loss(simulation_result: SimulationResult) -> list:
    res = []
    for snapshot in simulation_result.snapshots:
        res.append(
            snapshot.lp_with_just_hold_strategy.valuation - snapshot.lp_state.valuation
        )
    return res


def plot_impermanent_loss(
    period_alias: str,
    results: dict[str, ExperimentResult],
):
    """
    results: dict[str, ExperimentResult]
        keys -- experiment names
        values -- ExperimentResult
    """

    fig, ax = plt.subplots(figsize=(10, 6))

    for experiment_name, experiment_result in results.items():
        simulation_result = experiment_result.simulation_result
        sns.lineplot(
            x=simulation_result.timestamps,
            y=extract_impermanent_loss(simulation_result),
            ax=ax,
            label=f"Impermanent Loss ({experiment_name})",
        )

    fix_x_axis_labels(ax)

    plt.xlabel("Time")
    plt.ylabel("Impermanent Loss")

    plt.xticks(rotation=45)
    plt.title(f"Impermanent Loss over time, {period_alias}")
    plt.tight_layout()

    plt.show()


def get_single_experiment_summary(experiment_result: ExperimentResult) -> dict:
    simulation_result = experiment_result.simulation_result
    last_iu_state = simulation_result.snapshots[-1].user_states[UserType.INFORMED]
    last_uu_state = simulation_result.snapshots[-1].user_states[UserType.UNINFORMED]
    return {
        "iu_markout": last_iu_state.total_markout,
        "iu_trade_count": last_iu_state.trades_count,
        "iu_yield": last_iu_state.yield_markout(),
        "uu_markout": last_uu_state.total_markout,
        "uu_trade_count": last_uu_state.trades_count,
        "uu_yield": last_uu_state.yield_markout(),
        "lp_markout": simulation_result.snapshots[-1].lp_state.total_markout,
        "lp_yield": simulation_result.snapshots[-1].lp_state.yield_markout(),
        "impermanent_loss": extract_impermanent_loss(simulation_result)[-1],
    }


def get_experiments_summary_by_alias(
    results: dict[str, ExperimentResult],
) -> pd.DataFrame:
    """
    results: dict[str, ExperimentResult]
        keys -- experiment names
        values -- ExperimentResult
    """
    res = []
    for experiment_name, experiment_result in results.items():
        res.append(
            {"experiment_name": experiment_name}
            | get_single_experiment_summary(experiment_result)
        )
    df = pd.DataFrame(res)
    return df.round(2)


def get_experiments_summary_by_description(
    experiments_results: dict[ExperimentDescriptionT, ExperimentResult],
) -> pd.DataFrame:
    """
    Get a summary of the experiments.

    Args:
        experiments (dict[str, Experiment]): A dictionary of experiments.
        experiments_results (dict[str, ExperimentResult]): A dictionary of experiment results.
    """

    summaries = []
    for experiment_description, experiments_result in experiments_results.items():
        experiment_summary = get_single_experiment_summary(experiments_result)
        summaries.append(
            convert_experiment_key_to_dict(experiment_description) | experiment_summary
        )

    return pd.DataFrame(summaries).round(2)


def export_markouts_to_csv(
    period_alias: str,
    results: dict[str, ExperimentResult],
    output_dir: str = "csv_export",
):
    """
    Export IU markouts, LP markouts and impermanent loss time series to CSV.
    One CSV per metric with columns: timestamp + one column per fee algorithm.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamps = list(results.values())[0].simulation_result.timestamps

    # IU markouts
    iu_data = {"timestamp": timestamps}
    for name, er in results.items():
        iu_data[name] = extract_user_markouts(er.simulation_result, UserType.INFORMED)
    pd.DataFrame(iu_data).to_csv(
        os.path.join(output_dir, f"{period_alias}_iu_markouts.csv"), index=False
    )

    # LP markouts
    lp_data = {"timestamp": timestamps}
    for name, er in results.items():
        lp_data[name] = extract_lp_markouts(er.simulation_result)
    pd.DataFrame(lp_data).to_csv(
        os.path.join(output_dir, f"{period_alias}_lp_markouts.csv"), index=False
    )

    # Impermanent loss
    il_data = {"timestamp": timestamps}
    for name, er in results.items():
        il_data[name] = extract_impermanent_loss(er.simulation_result)
    pd.DataFrame(il_data).to_csv(
        os.path.join(output_dir, f"{period_alias}_impermanent_loss.csv"), index=False
    )


def export_fee_history_to_csv(
    experiment_result: ExperimentResult,
    fee_algo_name: str,
    period_alias: str,
    output_dir: str = "csv_export",
    first_updates: int | None = None,
):
    """
    Export fee rate history (a_to_b and b_to_a) to CSV.
    """
    os.makedirs(output_dir, exist_ok=True)
    snapshots = experiment_result.simulation_result.snapshots
    timestamps = experiment_result.simulation_result.timestamps
    if first_updates is not None:
        snapshots = snapshots[:first_updates]
        timestamps = timestamps[:first_updates]

    a_to_b_fees = [s.pool.fee_algorithm.a_to_b_exchange_fee_rate for s in snapshots]
    b_to_a_fees = [s.pool.fee_algorithm.b_to_a_exchange_fee_rate for s in snapshots]

    pd.DataFrame({
        "timestamp": timestamps,
        "a_to_b_fee_rate": a_to_b_fees,
        "b_to_a_fee_rate": b_to_a_fees,
    }).to_csv(
        os.path.join(output_dir, f"{period_alias}_{fee_algo_name}_fee_history.csv"),
        index=False,
    )


def export_prices_to_csv(
    results: dict[str, ExperimentResult],
    output_dir: str = "csv_export",
):
    """
    Export price_A, price_B and price ratio per period to CSV.
    """
    os.makedirs(output_dir, exist_ok=True)
    for period_alias, er in results.items():
        data = er.data
        df = pd.DataFrame({
            "time": data["time"] if "time" in data.columns else data.index,
            "price_A": data["price_A"],
            "price_B": data["price_B"],
            "price_ratio_A_B": data["price_A"] / data["price_B"],
        })
        df.to_csv(
            os.path.join(output_dir, f"{period_alias}_prices.csv"), index=False
        )
