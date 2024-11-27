from abc import ABC, abstractmethod
from typing import Optional
from pool.abstract_pool import Pool
from prices_snapshot import PricesSnapshot
from user_action import UserAction


class User(ABC):
    @abstractmethod
    def get_user_action(
        self,
        pool: Pool,
        network_fee: float,
        prices: PricesSnapshot,
    ) -> Optional[UserAction]:
        """
        Args:
        pool: Pool, the pool
        network_fee: float, the network fee
        prices: PricesSnapshot, the prices of tokens A and B

        Returns:
        """
        pass
