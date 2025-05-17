from concurrent.futures import ProcessPoolExecutor, as_completed
from experiments.run_experiment import run_experiment
from experiments.experiment import Experiment, ExperimentResult
from typing import Tuple, FrozenSet, Dict, Optional
from tqdm import tqdm

ExperimentDescriptionT = FrozenSet[Tuple[str, str]]


def get_experiment_key(
    experiment_description: dict[str, str],
) -> ExperimentDescriptionT:
    return frozenset(sorted(experiment_description.items()))


def convert_experiment_key_to_dict(
    experiment_key: ExperimentDescriptionT,
) -> dict[str, str]:
    return dict(experiment_key)


def run_multiple_experiments(
    experiments: Dict[ExperimentDescriptionT, Experiment],
    return_intermediate_results: bool = True,
    parallel: bool = False,
    max_workers: Optional[int] = None,
) -> Dict[ExperimentDescriptionT, ExperimentResult]:
    """
    Run multiple experiments and return the results.

    Args:
        experiments (dict[ExperimentDescriptionT, Experiment]): A dictionary of experiments to run.
        return_intermediate_results (bool): Whether to return intermediate results.
        parallel (bool): Whether to run experiments in parallel.
        max_workers (int, optional): The maximum number of threads to use for parallel execution.
    """
    results = {}

    if parallel:
        assert (
            max_workers is not None
        ), "max_workers must be specified when parallel=True"

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_experiment = {
                executor.submit(
                    run_experiment,
                    experiment,
                    return_intermediate_results=return_intermediate_results,
                ): name
                for name, experiment in experiments.items()
            }

            for future in tqdm(
                as_completed(future_to_experiment),
                total=len(future_to_experiment),
                desc="Running Experiments",
            ):
                experiment_name = future_to_experiment[future]
                try:
                    results[experiment_name] = future.result()
                except Exception as e:
                    results[experiment_name] = f"Error: {e}"  # Handle errors gracefully
    else:
        for experiment_name, experiment in experiments.items():
            results[experiment_name] = run_experiment(
                experiment, return_intermediate_results=return_intermediate_results
            )

    return results
