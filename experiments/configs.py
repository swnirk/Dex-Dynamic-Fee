from experiments.experiment import HistoricalDataDescription, UninformedUsersConfig
from datetime import datetime
from user.uninformed_user import UninformedUser

DATA_SOURCE_BY_ALIAS = {
    "volatile_market": HistoricalDataDescription(
        start_time=datetime(2024, 3, 1, 12, 0, 0),
        end_time=datetime(2024, 3, 31, 12, 0, 0),
        candle_interval="1min",
    ),
    "calm_market": HistoricalDataDescription(
        start_time=datetime(2024, 8, 1, 12, 0, 0),
        end_time=datetime(2024, 8, 31, 12, 0, 0),
        candle_interval="1min",
    ),
    "bull_market": HistoricalDataDescription(
        start_time=datetime(2024, 11, 1, 12, 0, 0),
        end_time=datetime(2024, 11, 30, 12, 0, 0),
        candle_interval="1min",
    ),
    "bear_market": HistoricalDataDescription(
        start_time=datetime(2024, 4, 1, 12, 0, 0),
        end_time=datetime(2024, 4, 30, 12, 0, 0),
        candle_interval="1min",
    ),
}


DEFAULT_UNINFORMED_USERS_CONFIG = UninformedUsersConfig(
    uninformed_user=UninformedUser(),
    probability_of_trade=0.5 * 12 / 60,
    n_users=1,
)
