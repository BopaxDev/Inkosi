from dataclasses import dataclass
from datetime import datetime
from typing import Any

from inkosi.database.mongodb.schemas import Position
from inkosi.utils.utils import EnhancedStrEnum

TICKS_DATETIME_INDEX: int = 0
TICKS_BID_INDEX: int = 1
TICKS_ASK_INDEX: int = 2


class SourceType(EnhancedStrEnum):
    """
    Enumeration of data source types.

    Attributes:
        SQL (str): Represents a SQL data source.
        CSV (str): Represents a CSV data source.
        HDF (str): Represents an HDF data source.
        PARQUET (str): Represents a Parquet data source.
    """

    SQL: str = "sql"
    CSV: str = "csv"
    HDF: str = "hdf"
    PARQUET: str = "parquet"
    ASSET: str = "asset"


class TradeResult(EnhancedStrEnum):
    """
    Enumeration of trade result types.

    Attributes:
        PROFIT (str): Represents a profitable trade result.
        LOSS (str): Represents a losing trade result.
        PENDING (str): Represents a pending trade result.
    """

    PROFIT: str = "profit"
    LOSS: str = "loss"
    PENDING: str = "pending"


class TradeStatus(EnhancedStrEnum):
    """
    Enumeration of trade status types.

    Attributes:
        CLOSED (str): Represents a closed trade status.
        PENDING (str): Represents a pending trade status.
    """

    CLOSED: str = "closed"
    PENDING: str = "pending"


@dataclass
class BacktestRecord:
    """
    Data class representing a backtest record.

    Attributes:
        direction (Position): The trading direction (buy/sell).
        entry_point (float): The entry point of the trade.
        entry_point_index (int): The index of the entry point in the dataset.
        take_profit (float): The take-profit level of the trade.
        stop_loss (float): The stop-loss level of the trade.
        price_close (float): The closing price of the trade.
        price_close_index (int): The index of the closing price in the dataset.
        time_opening (datetime): The timestamp when the trade was opened.
        time_closing (datetime): The timestamp when the trade was closed.
        status (TradeStatus): The status of the trade (closed/pending).
        result (TradeResult): The result of the trade (profit/loss/pending).
    """

    direction: Position
    entry_point: float
    entry_point_index: int
    take_profit: float
    stop_loss: float
    price_close: float
    price_close_index: int
    time_opening: datetime
    time_closing: datetime
    status: TradeStatus
    result: TradeResult


@dataclass
class BacktestRequest:
    """
    Data class representing a backtest request.

    Attributes:
        starting_indexes (list[int]): List of starting indexes for backtesting.
        direction (list[Position]): List of trading directions for backtesting.
        take_profits (list[float]): List of take-profit levels for backtesting.
        stop_losses (list[float]): List of stop-loss levels for backtesting.
        dataset (Dataset): The dataset used for backtesting.
    """

    starting_indexes: list[int]
    direction: list[Position]
    take_profits: list[float]
    stop_losses: list[float]
    dataset: Any
