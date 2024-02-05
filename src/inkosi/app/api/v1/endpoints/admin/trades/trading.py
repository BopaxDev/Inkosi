from dataclasses import asdict

from bson.objectid import ObjectId
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from inkosi.api.metatrader import close_position, open_position
from inkosi.api.schemas import (
    CloseRequestTradeResult,
    OpenRequestTradeResult,
    StatusTradeResult,
)
from inkosi.database.mongodb.database import MongoDBCrud
from inkosi.database.mongodb.schemas import CloseTradeRequest, TradeRequest

router = APIRouter(
    prefix="/trading",
)


@router.post(
    path="/position",
    summary="",
)
async def position_opening(
    order: TradeRequest,
) -> JSONResponse:
    mongodb = MongoDBCrud()

    result: OpenRequestTradeResult = open_position(
        order=order,
        allow_no_risk_limits=False,
    )
    match result.status:
        case StatusTradeResult.ORDER_FILLED:
            order.deal_id = result.deal_id
            order.volume = result.volume
            order.status = True
            record_id: ObjectId | None = mongodb.add_trade(order)

            return JSONResponse(
                content={
                    "detail": "Position correctly opened",
                    "record": str(record_id),
                },
                status_code=status.HTTP_200_OK,
            )
        case _:
            return JSONResponse(
                content={
                    "detail": "Unable to open the position",
                    "message": result.detail,
                    "error": result.error,
                    "error_code": result.error_code,
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@router.get(
    path="/position",
    summary="",
)
async def position_information(
    opened: bool | None = None,
) -> JSONResponse:
    mongodb = MongoDBCrud()

    result: OpenRequestTradeResult = mongodb.get_all_trades(opened=opened)
    return JSONResponse(
        content=result,
        status_code=status.HTTP_200_OK,
    )


@router.delete(
    path="/position",
    summary="",
)
async def position_closing(
    close_trade_request: CloseTradeRequest,
) -> JSONResponse:
    mongodb = MongoDBCrud()

    record = mongodb.get_deal_from_id(record_id=close_trade_request.record_id)
    if record is None:
        return JSONResponse(
            content={
                "detail": "Unable to find any record through the given id",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    result: CloseRequestTradeResult = close_position(order=record)
    match result.status:
        case StatusTradeResult.ORDER_FILLED:
            mongodb.update_trade(
                trade_id=close_trade_request.record_id,
                updates=TradeRequest(
                    status=False,
                    commission_broker=result.fee,
                    returns=result.profit,
                ),
            )

            return JSONResponse(
                content={
                    "detail": "Position correctly closed",
                },
                status_code=status.HTTP_200_OK,
            )
        case _:
            return JSONResponse(
                content={
                    "detail": "Unable to properly close the position",
                    "result": asdict(result),
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
