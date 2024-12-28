from experiments.experiment import ExperimentData, UninformedUsersConfig
from datetime import datetime
from user.uninformed_user import UninformedUser

DATA_SOURCE_BY_ALIAS = {
    "volatile_market": ExperimentData(
        start_time=datetime(2024, 3, 1, 12, 0, 0),
        end_time=datetime(2024, 3, 31, 12, 0, 0),
    ),
    "calm_market": ExperimentData(
        start_time=datetime(2024, 8, 1, 12, 0, 0),
        end_time=datetime(2024, 8, 31, 12, 0, 0),
    ),
    "bull_market": ExperimentData(
        start_time=datetime(2024, 11, 1, 12, 0, 0),
        end_time=datetime(2024, 11, 30, 12, 0, 0),
    ),
    "bear_market": ExperimentData(
        start_time=datetime(2024, 4, 1, 12, 0, 0),
        end_time=datetime(2024, 4, 30, 12, 0, 0),
    ),
}


DEFAULT_UNINFORMED_USERS_CONFIG = UninformedUsersConfig(
    uninformed_user=UninformedUser(),
    probability_of_trade=0.5,
    n_users=1,
)
