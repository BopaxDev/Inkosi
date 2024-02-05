from dataclasses import dataclass
from enum import IntEnum


class StatusTradeResult(IntEnum):
    """
    Enumeration representing status codes for trade results.

    Attributes:
        ORDER_FILLED (int): Trade order filled successfully.
        NO_TICKER_PROVIDED (int): No ticker provided for the trade operation.
        TICKER_NOT_FOUND (int): Ticker not found in the available symbols.
        NO_VOLUME_PROVIDED (int): No volume provided for the trade operation.
        NO_OPERATION_SPECIFIED (int): No specific trade operation (buy/sell) specified.
        NO_TAKE_PROFIT_SPECIFIED (int): No take profit value specified for the trade.
        NO_STOP_LOSS_SPECIFIED (int): No stop loss value specified for the trade.
        NO_ORDER_FILLING (int): No order filling type specified for the trade.
        NO_FILLING_TYPE_FOUND (int): No valid filling type found for the trade.
        MARKET_CLOSED (int): The market is closed, and the trade cannot be executed.
        NO_DEAL_ID_FOUND (int): No deal ID found for the trade result.
        NO_POSITION_ID_FOUND (int): No position ID found for the trade result.

    Note:
        This enumeration defines status codes for various trade results.
        Each status code represents a specific outcome or condition related to trade
        operations.
    """

    ORDER_FILLED: int = 0
    NO_TICKER_PROVIDED: int = -1
    TICKER_NOT_FOUND: int = -2
    NO_VOLUME_PROVIDED: int = -3
    NO_OPERATION_SPECIFIED: int = -4
    NO_TAKE_PROFIT_SPECIFIED: int = -5
    NO_STOP_LOSS_SPECIFIED: int = -6
    NO_ORDER_FILLING: int = -7
    NO_FILLING_TYPE_FOUND: int = -8
    MARKET_CLOSED: int = -9
    NO_DEAL_ID_FOUND: int = -10
    NO_POSITION_ID_FOUND: int = -11


@dataclass
class OpenRequestTradeResult:
    """
    Data class representing the result of an open trade request.

    Attributes:
        detail (str): A detailed description or message regarding the trade result.
        status (StatusTradeResult): The status of the trade result, indicating
            success or failure.
        trade_id (int, optional): The ID of the opened trade, if successful.
        deal_id (int, optional): The ID of the deal associated with the opened trade, if
            successful.
        volume (float, optional): The volume of the opened trade, if successful.
        error (str, optional): An error message if the trade request encountered an
            error.
        error_code (int, optional): The error code associated with the error, if
            applicable.

    Note:
        This data class is designed to hold the result of an open trade request.
        It includes details such as a descriptive message, the status of the trade
        result, the trade ID, deal ID, volume, error message, and error code.
    """

    detail: str
    status: StatusTradeResult
    trade_id: int | None = None
    deal_id: int | None = None
    volume: float | None = None
    error: str | None = None
    error_code: int | None = None


@dataclass
class CloseRequestTradeResult:
    """
    Data class representing the result of a close trade request.

    Attributes:
        detail (str): A detailed description or message regarding the trade result.
        status (StatusTradeResult): The status of the trade result, indicating
            success or failure.
        profit (float, optional): The profit obtained from closing the trade,
            if successful.
        fee (float, optional): The fee associated with closing the trade, if successful.
        error (str, optional): An error message if the trade request encountered an
            error.
        error_code (int, optional): The error code associated with the error, if
            applicable.

    Note:
        This data class is designed to hold the result of a close trade request.
        It includes details such as a descriptive message, the status of the trade
        result, profit, fee, error message, and error code.
    """

    detail: str
    status: StatusTradeResult
    profit: float | None = None
    fee: float | None = None
    error: str | None = None
    error_code: int | None = None
