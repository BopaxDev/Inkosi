from datetime import date, datetime, timedelta

import pandas as pd
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from inkosi.app.schemas import Returns
from inkosi.database.mongodb.database import MongoDBCrud
from inkosi.database.mongodb.schemas import ReturnRequest
from inkosi.database.postgresql.database import PostgreSQLCrud
from inkosi.database.postgresql.schemas import FundInformation

router = APIRouter()


@router.post(
    path="/returns",
    summary="",
    response_model=Returns,
)
async def returns(
    return_request: ReturnRequest,
) -> Returns:
    postgres = PostgreSQLCrud()
    funds_information: FundInformation = postgres.get_fund_information(
        return_request.fund_name
    )

    if isinstance(return_request.date_from, str):
        return_request.date_from = datetime.strptime(
            return_request.date_from,
            "%d/%m/%Y",
        )

    if isinstance(return_request.date_to, str):
        return_request.date_to = datetime.strptime(
            return_request.date_to,
            "%d/%m/%Y",
        )

    if len(funds_information) != 1:
        return JSONResponse(
            content={"detail": "Unable to find the correct information"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    fund_information = funds_information[0]

    initial_capital: float = sum(fund_information.capital_distribution.values())
    # cumulative_returns: float = initial_capital

    mongodb = MongoDBCrud()
    result = mongodb.get_returns(fund=fund_information.fund_name)

    cumulative_commissions_fund: float = 0.0
    cumulative_commissions_broker: float = 0.0
    absolute_returns: float = 0.0

    results_parsed: dict[str, list] = {}

    for record in result:
        __datetime: datetime | None = record.get("datetime")
        if not __datetime:
            continue

        if not isinstance(__datetime, datetime):
            continue

        __datetime = date(__datetime.year, __datetime.month, __datetime.day)
        __datetime_str = __datetime.strftime("%d/%m/%Y")
        value: list[float] = results_parsed.get(__datetime_str, [0.0, 0.0, 0.0])

        value[0] += (
            0.0
            if not record.get("commission_fund", None)
            else record.get("commission_fund", None)
        )
        value[1] += (
            0.0
            if not record.get("commission_broker", None)
            else record.get("commission_broker", None)
        )
        value[2] += (
            0.0 if not record.get("returns", None) else record.get("returns", None)
        )

        cumulative_commissions_fund += value[0]
        cumulative_commissions_broker += value[1]
        absolute_returns += value[2]

        results_parsed[__datetime_str] = value

    raw_dates_range = pd.date_range(
        start=return_request.date_from,
        end=return_request.date_to,
        freq="D",
    )
    raw_returns = {}

    for _date in raw_dates_range:
        __date_str = _date.strftime("%d/%m/%Y")
        previous_value = raw_returns.get(
            (_date - timedelta(days=1)).strftime("%d/%m/%Y"),
            initial_capital,
        )

        result_on_day: list[float] = results_parsed.get(__date_str, [0.0, 0.0, 0.0])

        raw_returns[__date_str] = previous_value + result_on_day[2]

    return JSONResponse(
        content={
            "initial_capital": initial_capital,
            "cumulative_commissions_fund": cumulative_commissions_fund,
            "cumulative_commissions_broker": cumulative_commissions_broker,
            "absolute_returns": absolute_returns,
            "raw_returns": raw_returns,
        },
        status_code=status.HTTP_200_OK,
    )
