from experiments.experiment import ExperimentData, UninformedUsersConfig
from datetime import datetime
from user.uninformed_user import UninformedUser

DATA_SOURCE_BY_ALIAS = {
    "volatile_market": ExperimentData(
        start_time=datetime(2022, 11, 10, 12, 0, 0),
        end_time=datetime(2022, 11, 16, 12, 0, 0),
    ),
    "calm_market": ExperimentData(
        start_time=datetime(2023, 7, 15, 12, 0, 0),
        end_time=datetime(2023, 7, 21, 12, 0, 0),
    ),
    "bull_market": ExperimentData(
        start_time=datetime(2023, 9, 25, 12, 0, 0),
        end_time=datetime(2023, 10, 2, 12, 0, 0),
    ),
    "bear_market": ExperimentData(
        start_time=datetime(2023, 10, 3, 12, 0, 0),
        end_time=datetime(2023, 10, 11, 12, 0, 0),
    ),
}

DEFAULT_UNINFORMED_USERS_CONFIG = UninformedUsersConfig(
    uninformed_user=UninformedUser(),
    probability_of_trade=0.5,
    n_users=1,
)
