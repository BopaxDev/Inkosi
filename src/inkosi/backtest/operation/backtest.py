import numpy as np
import pandas as pd
import pandas_ta as ta
from numpy.typing import NDArray

from inkosi.backtest.operation.models import (
    TICKS_ASK_INDEX,
    TICKS_BID_INDEX,
    BacktestRecord,
    BacktestRequest,
    TradeResult,
    TradeStatus,
)
from inkosi.backtest.operation.schemas import (
    AvailableRawColumns,
    AvailableTechincalIndicators,
    ComparisonElement,
    Elements,
    Filter,
    Relation,
)
from inkosi.database.mongodb.schemas import Position
from inkosi.log.log import Logger
from inkosi.utils.settings import get_technical_indicators_values

logger = Logger(
    module_name="backtest",
    package_name="backtest",
    database=False,
)


def technical_column(
    data_frame: pd.DataFrame,
    column_type: AvailableRawColumns | AvailableTechincalIndicators | None,
    additional_information: dict = {},
) -> NDArray | None:
    if AvailableRawColumns.has(column_type):
        return data_frame[column_type]

    match column_type:
        case AvailableTechincalIndicators.SMA:
            return data_frame.ta.sma(
                close=data_frame[Elements.CLOSE_PRICE],
                length=additional_information.get(
                    Elements.PERIOD,
                    get_technical_indicators_values().MovingAveragePeriod,
                ),
            ).to_numpy()
        case AvailableTechincalIndicators.WMA:
            return data_frame.ta.wma(
                close=data_frame[Elements.CLOSE_PRICE],
                length=additional_information.get(
                    Elements.PERIOD,
                    get_technical_indicators_values().MovingAveragePeriod,
                ),
            ).to_numpy()
        case AvailableTechincalIndicators.EMA:
            return data_frame.ta.ema(
                close=data_frame[Elements.CLOSE_PRICE],
                length=additional_information.get(
                    Elements.PERIOD,
                    get_technical_indicators_values().MovingAveragePeriod,
                ),
            ).to_numpy()
        case _:
            return data_frame[column_type]


def filter_dataset(
    data_frame: pd.DataFrame,
    filters: list[Filter],
) -> NDArray:
    indexes_list = set(data_frame.index)

    for _filter in filters:
        first_element: ComparisonElement = _filter.first_element
        second_element: ComparisonElement = _filter.second_element
        relation: Relation = _filter.relation

        first_column: NDArray = technical_column(
            data_frame=data_frame,
            column_type=first_element.get(Elements.ELEMENT),
            additional_information=first_element,
        )

        second_column: NDArray = technical_column(
            data_frame,
            column_type=second_element.get(Elements.ELEMENT),
            additional_information=second_element,
        )

        match relation:
            case Relation.GREATER:
                _indexes = np.nonzero(first_column > second_column)
            case Relation.GREATER_THAN:
                _indexes = np.nonzero(first_column >= second_column)
            case Relation.LESS:
                _indexes = np.nonzero(first_column < second_column)
            case Relation.LESS_THAN:
                _indexes = np.nonzero(first_column <= second_column)
            case Relation.EQUAL:
                _indexes = np.nonzero(first_column == second_column)
            case _:
                return np.array([])

        indexes_list.intersection_update(_indexes[0])

    return np.array(list(indexes_list))


def checker(
    dataset: NDArray,
    direction: Position,
    starting_index: int,
    entry_point: float,
    take_profit: float,
    stop_loss: float,
    delta: int = 20000,
) -> int | None:
    current_index = starting_index
    last_index = dataset.shape[0]

    if not Position.has(direction):
        logger.critical("Backtest Interrupted... Dataset records exhausted")
        return

    while current_index < last_index:
        if direction == Position.BUY:
            tmp_dataset = dataset[
                current_index : current_index + delta, TICKS_BID_INDEX
            ]
            result = np.argmax((tmp_dataset >= entry_point + take_profit))

        elif direction == Position.SELL:
            tmp_dataset = dataset[
                current_index : current_index + delta, TICKS_ASK_INDEX
            ]
            result = np.argmax((tmp_dataset <= entry_point - abs(stop_loss)))

        if not result:
            current_index += delta
        else:
            return current_index + result


def backtest(request: BacktestRequest) -> list[BacktestRecord] | None:
    result: list[BacktestRecord] = []
    dataset: NDArray | None = request.dataset.get_dataset()
    if dataset is None:
        return None

    n_dataset: int = dataset.shape[0]

    if len(request.direction) != len(request.starting_indexes):
        logger.error(
            "The length of the 'Direction' vector is not equal to the 'Starting"
            " Indexes' vector"
        )
        return

    for occurence, direction, take_profit, stop_loss in zip(
        request.starting_indexes,
        request.direction,
        request.take_profits,
        request.stop_losses,
    ):
        if occurence + 1 > n_dataset - 1:
            logger.critical("Backtest Interrupted... Dataset records exhausted")
            break

        entry_point_index: int = occurence + 1

        match direction:
            case Position.BUY:
                entry_point_price: float = dataset[entry_point_index, TICKS_BID_INDEX]
            case Position.SELL:
                entry_point_price: float = dataset[entry_point_index, TICKS_ASK_INDEX]
            case _:
                continue

        result_up = checker(
            dataset,
            Position.BUY,
            entry_point_index,
            entry_point_price,
            take_profit,
            stop_loss,
        )
        result_down = checker(
            dataset,
            Position.SELL,
            entry_point_index,
            entry_point_price,
            take_profit,
            stop_loss,
        )

        if result_up is None or result_down is None:
            continue

        if direction == Position.BUY:
            if result_down == 0:
                trade_result = TradeResult.PROFIT
                trade_status = TradeStatus.CLOSED
            elif result_up == 0:
                trade_result = TradeResult.LOSS
                trade_status = TradeStatus.CLOSED
            else:
                trade_result = TradeResult.PENDING
                trade_status = TradeStatus.PENDING

            if result_up < result_down:
                trade_result = TradeResult.PROFIT
                trade_status = TradeStatus.CLOSED
            else:
                trade_result = TradeResult.LOSS
                trade_status = TradeStatus.CLOSED
        elif direction == Position.SELL:
            if result_down == 0:
                trade_result = TradeResult.LOSS
                trade_status = TradeStatus.CLOSED
            elif result_up == 0:
                trade_result = TradeResult.PROFIT
                trade_status = TradeStatus.CLOSED
            else:
                trade_result = TradeResult.PENDING
                trade_status = TradeStatus.PENDING
            if result_up < result_down:
                trade_result = TradeResult.LOSS
                trade_status = TradeStatus.CLOSED
            else:
                trade_result = TradeResult.PROFIT
                trade_status = TradeStatus.CLOSED
        else:
            logger.critical(
                f"Unable to identify the specified 'Direction' parameter: {direction}"
            )

        result.append(
            BacktestRecord(
                direction=direction,
                entry_point=entry_point_price,
                entry_point_index=entry_point_index,
                take_profit=take_profit,
                stop_loss=stop_loss,
                price_close=...,
                price_close_index=...,
                time_opening=...,
                time_closing=...,
                status=trade_status,
                result=trade_result,
            )
        )

    return result
