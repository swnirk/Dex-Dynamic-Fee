import seaborn as sns
import matplotlib.pyplot as plt
from simulation.simulation import UserType, SimulationResult
from experiments.experiment import ExperimentResult
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


def plot_participants_markouts(
    period_alias: str,
    results: dict[str, ExperimentResult],
):
    """
    results: dict[str, ExperimentResult]
        keys -- experiment names
        values -- ExperimentResult
    """

    fig, ax = plt.subplots(figsize=(10, 6))

    for user_type in UserType:
        for experiment_name, experiment_result in results.items():
            simulation_result = experiment_result.simulation_result
            user_type_str = (
                "Informed" if user_type == UserType.INFORMED else "Uninformed"
            )
            sns.lineplot(
                x=simulation_result.timestamps,
                y=extract_user_markouts(simulation_result, user_type),
                ax=ax,
                label=f"{user_type_str} ({experiment_name})",
                
            )

    for experiment_name, experiment_result in results.items():
        simulation_result = experiment_result.simulation_result
        sns.lineplot(
            x=simulation_result.timestamps,
            y=extract_lp_markouts(simulation_result),
            ax=ax,
            label=f"LP ({experiment_name})",
        )

    fix_x_axis_labels(ax)

    plt.xlabel("Time")
    plt.ylabel("Markout")

    plt.xticks(rotation=45)
    plt.title(f"Markouts over time, {period_alias}")
    plt.tight_layout()

    plt.show()


def extract_impermanent_loss(simulation_result: SimulationResult) -> list:
    res = []
    for snapshot in simulation_result.snapshots:
        res.append(
            snapshot.lp_state.valuation - snapshot.lp_with_just_hold_strategy.valuation
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


def get_experiment_summary(
    results: dict[str, ExperimentResult],
) -> pd.DataFrame:
    """
    results: dict[str, ExperimentResult]
        keys -- experiment names
        values -- ExperimentResult
    """
    res = []
    for experiment_name, experiment_result in results.items():
        simulation_result = experiment_result.simulation_result
        res.append(
            {
                "experiment_name": experiment_name,
                "informed_user_markout": simulation_result.snapshots[-1]
                .user_states[UserType.INFORMED]
                .total_markout,
                "uninformed_user_markout": simulation_result.snapshots[-1]
                .user_states[UserType.UNINFORMED]
                .total_markout,
                "lp_markout": simulation_result.snapshots[-1].lp_state.total_markout,
                "impermanent_loss": simulation_result.snapshots[-1].lp_state.valuation
                - simulation_result.snapshots[-1].lp_with_just_hold_strategy.valuation,
            }
        )
    return pd.DataFrame(res)
