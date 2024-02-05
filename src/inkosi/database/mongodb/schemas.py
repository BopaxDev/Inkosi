from dataclasses import dataclass
from datetime import date

from inkosi.utils.utils import EnhancedStrEnum


class OrderType(EnhancedStrEnum):
    """
    Enumeration representing types of trading orders.

    Attributes:
        MARKET_ORDER (str): Type of market order.
        SCHEDULED (str): Type of scheduled order.
    """

    MARKET_ORDER: str = "market_order"
    SCHEDULED: str = "scheduled"


class Position(EnhancedStrEnum):
    """
    Enumeration representing positions in trading.

    Attributes:
        BUY (str): Represents a buy position.
        SELL (str): Represents a sell position.
    """

    BUY: str = "buy"
    SELL: str = "sell"


@dataclass
class TradeRequest:
    """
    Data class representing a trade request.

    Attributes:
        fund (int | None): Identifier for the fund involved in the trade.
        portfolio_manager (int | None): Identifier for the portfolio manager initiating
        the trade.
        ats (str | None): Identifier for the automated trading system (ATS) used.
        investors (dict | None): Information about the investors involved in the trade.
        order_type (OrderType | None): Type of the trading order
        (Market Order or Scheduled).
        operation (Position | None): Position type (Buy or Sell).
        ticker (str | None): Ticker symbol for the financial instrument.
        take_profit (float | None): Desired take-profit level for the trade.
        stop_loss (float | None): Desired stop-loss level for the trade.
        entry_point (float | None): Entry point for the trade.
        close_price (float | None): Closing price for the trade.
        volume (float | None): Volume of the trade.
        returns (float | None): Returns from the trade.
        commission_broker (float | None): Broker commission for the trade.
        commission_fund (float | None): Fund commission for the trade.
        risk_management (bool | None): Flag indicating the use of risk management.
        deal_id (int | None): Identifier for the trade deal.
        notes (dict | None): Additional notes or information about the trade.
        status (bool | None): Status of the trade (e.g., open or closed).
    """

    fund: str | None = None
    portfolio_manager: int | None = None
    ats: str | None = None
    investors: dict | None = None
    order_type: OrderType | None = None
    operation: Position | None = None
    ticker: str | None = None
    take_profit: float | None = None
    stop_loss: float | None = None
    entry_point: float | None = None
    close_price: float | None = None
    volume: float | None = None
    returns: float | None = None
    commission_broker: float | None = None
    commission_fund: float | None = None
    risk_management: bool | None = None
    deal_id: int | None = None
    notes: dict | None = None
    status: bool | None = None


@dataclass
class CloseTradeRequest:
    """
    Data class representing a request to close a trade.

    Attributes:
        record_id (str): Identifier for the trade record to be closed.
    """

    record_id: str


@dataclass
class ReturnRequest:
    """
    Data class representing a request for returns information.

    Attributes:
        fund_name (str): Name of the fund for which returns are requested.
        date_from (date): Start date for the returns calculation.
        date_to (date): End date for the returns calculation.
    """

    fund_name: str
    date_from: date | str
    date_to: date | str
