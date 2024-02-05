import random
import time
from functools import lru_cache

from inkosi.api.schemas import (
    CloseRequestTradeResult,
    OpenRequestTradeResult,
    StatusTradeResult,
)
from inkosi.database.mongodb.schemas import Position, TradeRequest
from inkosi.log.log import Logger
from inkosi.portfolio.risk_management import RiskManagement
from inkosi.utils.settings import get_environmental_settings

try:
    import MetaTrader5 as mt5

    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


logger = Logger(
    module_name="metatrader5",
    package_name="api",
)


def check_mt5_available() -> bool:
    """
    Check the availability of MetaTrader 5 (MT5) connection.

    Returns:
        (bool): Returns True if MT5 is available and the connection is established
            successfully, False otherwise.

    Note:
        This function checks for the availability of MetaTrader 5 (MT5) by verifying
        the `MT5_AVAILABLE` flag. If the flag is False, the function returns False.

        If the flag is True, the function attempts to initialize a connection to the
        MT5 broker using the server, account, and password information obtained from
        `get_environmental_settings()`.

        Returns True if the connection is established successfully, and False otherwise.
        In case of connection failure, an error message is logged using the logger.
    """

    if not MT5_AVAILABLE:
        return False

    if not mt5.initialize(
        server=get_environmental_settings().SERVER,
        login=get_environmental_settings().ACCOUNT,
        password=get_environmental_settings().PASSWORD,
    ):
        logger.error(
            "Unable to establish a connection to the Broker through the given"
            " credentials"
        )
        return False

    return True


def initialize() -> bool:
    """
    Initialize MetaTrader 5 (MT5) platform.

    Returns:
        (bool): True if initialization is successful, False otherwise.
    """

    return check_mt5_available()


def shutdown() -> None:
    """
    Shutdown MetaTrader 5 (MT5) platform.
    """

    check_mt5_available()
    mt5.shutdown()


@lru_cache
def get_all_symbols_available() -> list[str] | None:
    """
    Get a list of all available symbols on MetaTrader 5 (MT5) platform.

    Returns:
        (list[str] | None): A list of symbol names if available, or None if
            initialization fails.
    """

    if initialize():
        return [symbol._asdict().get("name", "") for symbol in list(mt5.symbols_get())]

    logger.critical("No symbols have been found")


def check_for_financial_product_existence(
    financial_product: str,
) -> bool:
    """
    Check if a financial product exists among the available symbols on MetaTrader 5
    (MT5) platform.

    Parameters:
        financial_product (str): The name of the financial product to check.

    Returns:
        (bool): True if the financial product exists, False otherwise.
    """

    symbols_list = get_all_symbols_available()
    if not symbols_list:
        return False

    return financial_product in symbols_list


def check_for_positions_opened_on_symbol(
    symbol: str,
) -> int | None:
    """
    Check for the number of open positions on a specific symbol on MetaTrader 5 (MT5)
    platform.

    Parameters:
        symbol (str): The symbol name to check for open positions.

    Returns:
        (int | None): The number of open positions on the symbol if available, or None
            if initialization fails.
    """
    if not initialize():
        return
    return mt5.positions_get(symbol=symbol)


def get_symbol_filling(
    symbol: str,
) -> int | None:
    """
    Get the filling mode for a specific symbol on MetaTrader 5 (MT5) platform.

    Parameters:
    symbol (str): The name of the symbol to retrieve filling mode information.

    Returns:
        (int | None): The filling mode constant (ORDER_FILLING_FOK, ORDER_FILLING_IOC,
            ORDER_FILLING_RETURN) if available, or None if initialization fails or the
            symbol information cannot be retrieved.
    """

    if not initialize() or not check_for_financial_product_existence(symbol):
        return

    match mt5.symbol_info(symbol)._asdict().get("filling_mode", None):
        case None:
            logger.error(
                f"Unable to fetch information regarding the symbol specified: {symbol}"
            )
            return
        case 1:
            return mt5.ORDER_FILLING_FOK
        case 2:
            return mt5.ORDER_FILLING_IOC
        case _:
            return mt5.ORDER_FILLING_RETURN


def get_ask_of_symbol(
    symbol: str,
) -> float:
    """
    Get the ask price of a specific symbol on MetaTrader 5 (MT5) platform.

    Parameters:
        symbol (str): The name of the symbol to retrieve the ask price.

    Returns:
        (float): The ask price if available, or recursively calls itself until a valid
            ask price is obtained.
    """

    ask = mt5.symbol_info_tick(symbol).ask
    if ask > 0:
        return ask
    else:
        get_ask_of_symbol(symbol)


def get_bid_of_symbol(
    symbol: str,
) -> float:
    """
    Get the bid price of a specific symbol on MetaTrader 5 (MT5) platform.

    Parameters:
        symbol (str): The name of the symbol to retrieve the bid price.

    Returns:
        (float): The bid price if available, or recursively calls itself until a valid
            bid price is obtained.
    """
    bid = mt5.symbol_info_tick(symbol).bid
    if bid > 0:
        return bid
    else:
        get_bid_of_symbol(symbol)


def check_symbol_market_opened(
    symbol: str,
) -> bool:
    """
    Check if the market for a specific symbol is open on MetaTrader 5 (MT5) platform.

    Parameters:
        symbol (str): The name of the symbol to check for market openness.

    Returns:
        (bool): True if the market is open for the symbol, False otherwise.
    """

    symbol_information = mt5.symbol_info(symbol)

    if not symbol_information:
        logger.error(
            f"Unable to fetch information regarding the symbol specified: {symbol}"
        )
        return False

    if symbol_information._asdict().get("time", 0) < int(time.time()) - 1:
        return False
    else:
        return True


def open_position(
    order: TradeRequest,
    allow_no_risk_limits: bool,
) -> OpenRequestTradeResult:
    risk_management = RiskManagement()

    if order.ticker is None:
        return OpenRequestTradeResult(
            detail="No Ticker has been provided",
            status=StatusTradeResult.NO_TICKER_PROVIDED,
        )

    if not check_for_financial_product_existence(order.ticker):
        return OpenRequestTradeResult(
            detail="Ticker provided doesn't exist",
            status=StatusTradeResult.TICKER_NOT_FOUND,
        )

    if not check_symbol_market_opened(order.ticker):
        return OpenRequestTradeResult(
            detail="Market currently closed",
            status=StatusTradeResult.MARKET_CLOSED,
        )

    if not order.risk_management:
        volume: float = risk_management.compute_volume()
    else:
        volume: float | None = order.volume
        if not volume:
            return OpenRequestTradeResult(
                detail="No volume has been provided",
                status=StatusTradeResult.NO_VOLUME_PROVIDED,
            )

    match order.operation:
        case Position.BUY:
            position = mt5.POSITION_TYPE_BUY
            price: float = get_ask_of_symbol(symbol=order.ticker)
        case Position.SELL:
            position = mt5.POSITION_TYPE_SELL
            price: float = get_bid_of_symbol(symbol=order.ticker)
        case _:
            return OpenRequestTradeResult(
                detail="No specified operation has not been recognised",
                status=StatusTradeResult.NO_OPERATION_SPECIFIED,
            )

    trade_id: int = random.randint(100000000, 999999999)

    filling = get_symbol_filling(order.ticker)

    if filling is None:
        return OpenRequestTradeResult(
            detail="Unable to fetch the filling type for the specified ticker",
            status=StatusTradeResult.NO_FILLING_TYPE_FOUND,
        )

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": order.ticker,
        "volume": volume,
        "type": position,
        "price": price,
        "deviation": 20,
        "magic": trade_id,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling,
    }

    take_profit: float = 0.0
    stop_loss: float = 0.0

    match order.take_profit:
        case float():
            take_profit = (
                price + order.take_profit
                if position == mt5.POSITION_TYPE_BUY
                else price - order.take_profit
            )

        case _:
            take_profit: float | None = risk_management.adjust_take_profit()
            if not take_profit:
                if not allow_no_risk_limits:
                    return OpenRequestTradeResult(
                        detail="No Take Profit has been specified",
                        status=StatusTradeResult.NO_TAKE_PROFIT_SPECIFIED,
                    )
            else:
                take_profit = (
                    price + take_profit
                    if position == mt5.POSITION_TYPE_BUY
                    else price - take_profit
                )
                request["tp"] = take_profit

    match order.stop_loss:
        case float():
            stop_loss = (
                price - order.stop_loss
                if position == mt5.POSITION_TYPE_BUY
                else price + order.stop_loss
            )
            request["sl"] = stop_loss
        case _:
            stop_loss: float | None = risk_management.adjust_stop_loss()

            if not stop_loss:
                if not allow_no_risk_limits:
                    return OpenRequestTradeResult(
                        detail="No Stop Loss has been specified",
                        status=StatusTradeResult.NO_STOP_LOSS_SPECIFIED,
                    )
            else:
                request["sl"] = (
                    price - stop_loss
                    if position == mt5.POSITION_TYPE_BUY
                    else price + stop_loss
                )

    order_request = mt5.order_send(request)

    if not order_request:
        return OpenRequestTradeResult(
            detail="Unable to correctly fill the order",
            status=StatusTradeResult.NO_ORDER_FILLING,
            error="An error occurred while filling the order",
        )

    retcode = order_request._asdict().get("retcode", -1)
    deal_id = order_request._asdict().get("deal", -1)

    if retcode != mt5.TRADE_RETCODE_DONE or deal_id == -1:
        return CloseRequestTradeResult(
            detail="Unable to correctly fill the order",
            status=StatusTradeResult.NO_ORDER_FILLING,
            error="An error occurred while filling the order",
            error_code=None if not order_request else retcode,
        )
    else:
        return OpenRequestTradeResult(
            detail="Order correctly filled",
            status=StatusTradeResult.ORDER_FILLED,
            trade_id=trade_id,
            deal_id=deal_id,
            volume=volume,
        )


def close_position(
    order: TradeRequest,
) -> CloseRequestTradeResult:
    initialize()
    deal = mt5.history_deals_get(ticket=order.deal_id)

    if not deal:
        return CloseRequestTradeResult(
            detail="No Deal with the specified ID has been found",
            status=StatusTradeResult.NO_DEAL_ID_FOUND,
        )

    position_id = mt5.positions_get(ticket=deal[0].position_id)[0].ticket

    if not position_id:
        return CloseRequestTradeResult(
            detail="No Position with the specified ID has been found",
            status=StatusTradeResult.NO_POSITION_ID_FOUND,
        )

    volume: float | None = order.volume
    if not volume:
        return CloseRequestTradeResult(
            detail="No volume has been provided",
            status=StatusTradeResult.NO_VOLUME_PROVIDED,
        )

    match order.operation:
        case Position.BUY:
            position = mt5.POSITION_TYPE_SELL
            price: float = get_bid_of_symbol(symbol=order.ticker)
        case Position.SELL:
            position = mt5.POSITION_TYPE_BUY
            price: float = get_ask_of_symbol(symbol=order.ticker)
        case _:
            return CloseRequestTradeResult(
                detail="No specified operation has not been recognised",
                status=StatusTradeResult.NO_OPERATION_SPECIFIED,
            )

    filling = get_symbol_filling(order.ticker)

    if filling is None:
        return OpenRequestTradeResult(
            detail="Unable to fetch the filling type for the specified ticker",
            status=StatusTradeResult.NO_FILLING_TYPE_FOUND,
        )

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": order.ticker,
        "volume": volume,
        "type": position,
        "price": price,
        "position": position_id,
    }

    order_request = mt5.order_send(request)

    if not order_request:
        return CloseRequestTradeResult(
            detail="Unable to correctly fill the order",
            status=StatusTradeResult.NO_ORDER_FILLING,
            error="An error occurred while filling the order",
        )

    retcode = order_request._asdict().get("retcode", -1)
    deal_id = order_request._asdict().get("deal", -1)

    deal_information = mt5.history_deals_get(ticket=deal_id)

    if retcode != mt5.TRADE_RETCODE_DONE or not deal_information:
        return CloseRequestTradeResult(
            detail="Unable to correctly fill the order",
            status=StatusTradeResult.NO_ORDER_FILLING,
            error="An error occurred while filling the order",
            error_code=None if not order_request else retcode,
        )
    else:
        return CloseRequestTradeResult(
            detail="Order correctly filled",
            status=StatusTradeResult.ORDER_FILLED,
            profit=deal_information[0]._asdict().get("profit", None),
            fee=deal_information[0]._asdict().get("fee", None),
        )
