from dataclasses import dataclass
from abc import ABC, abstractmethod
from pool.liquidity_state import PoolLiquidityState, BalanceChange


@dataclass
class FeeAlgorithm(ABC):
    @abstractmethod
    def get_a_to_b_trade_fee(
        self, pool_state: PoolLiquidityState, x_user: float
    ) -> float:
        pass

    @abstractmethod
    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    @abstractmethod
    def process_trade(self, pool_balance_change: BalanceChange, pool_state: PoolLiquidityState) -> None:
        pass

    @abstractmethod
    def process_oracle_price(self, a_to_b_price: float) -> None:
        pass

    @abstractmethod
    def inverse(self) -> "FeeAlgorithm":
        pass

    @abstractmethod
    def process_block_end(self, pool_state: PoolLiquidityState) -> None:
        pass


@dataclass
class FeeKnownBeforeTradeAlgorithm(FeeAlgorithm, ABC):
    @abstractmethod
    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        pass

    @abstractmethod
    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    @abstractmethod
    def process_trade(self, pool_balance_change: BalanceChange, pool_state: PoolLiquidityState) -> None:
        pass

    @abstractmethod
    def process_oracle_price(self, a_to_b_price: float) -> None:
        pass

    @abstractmethod
    def inverse(self) -> "FeeKnownBeforeTradeAlgorithm":
        pass

    def get_b_to_a_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        return self.inverse().get_b_to_a_exchange_fee_rate(pool_state.inverse())

    def get_a_to_b_trade_fee(
        self, pool_state: PoolLiquidityState, x_user: float
    ) -> float:
        return self.get_a_to_b_exchange_fee_rate(pool_state) * x_user

    @abstractmethod
    def process_block_end(self, pool_state: PoolLiquidityState) -> None:
        pass


@dataclass
class FeeUnknownBeforeTradeAlgorithm(FeeAlgorithm, ABC):
    @abstractmethod
    def get_a_to_b_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        pass

    @abstractmethod
    def process_initial_pool_state(self, pool_state: PoolLiquidityState) -> None:
        pass

    @abstractmethod
    def process_trade(self, pool_balance_change: BalanceChange, pool_state: PoolLiquidityState) -> None:
        pass

    @abstractmethod
    def process_oracle_price(self, a_to_b_price: float) -> None:
        pass

    @abstractmethod
    def inverse(self) -> "FeeUnknownBeforeTradeAlgorithm":
        pass

    def get_b_to_a_exchange_fee_rate(self, pool_state: PoolLiquidityState) -> float:
        return self.inverse().get_b_to_a_exchange_fee_rate(pool_state.inverse())

    def get_a_to_b_trade_fee(
        self, pool_state: PoolLiquidityState, x_user: float
    ) -> float:
        return self.get_a_to_b_exchange_fee_rate(pool_state) * x_user

    @abstractmethod
    def process_block_end(self, pool_state: PoolLiquidityState) -> None:
        pass
