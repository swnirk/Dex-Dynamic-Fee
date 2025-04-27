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
