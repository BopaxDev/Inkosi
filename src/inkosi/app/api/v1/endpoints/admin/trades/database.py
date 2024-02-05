from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from inkosi.database.mongodb.database import MongoDBCrud
from inkosi.database.mongodb.schemas import TradeRequest

router = APIRouter()


@router.post(
    path="/trade",
    summary="",
)
async def add_trade(
    trade_request: TradeRequest,
) -> JSONResponse:
    mongodb = MongoDBCrud()
    result = mongodb.add_trade(trade_request)

    return JSONResponse(
        content={
            "detail": "Trade correctly added",
            "id": str(result),
        },
        status_code=status.HTTP_200_OK,
    )


@router.put(
    path="/trade/{trade_id}",
    summary="",
)
async def update_trade(
    trade_id: str,
    trade_request: TradeRequest,
) -> JSONResponse:
    mongodb = MongoDBCrud()
    result = mongodb.update_trade(
        trade_id=trade_id,
        updates=trade_request,
    )

    if not result:
        return JSONResponse(
            content={
                "detail": "Unable to update the document",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return JSONResponse(
        content={
            "detail": "Trade correctly added",
            "id": str(result.get("_id", "Not available")),
        },
        status_code=status.HTTP_200_OK,
    )


@router.get(
    path="/trade/{trade_id}",
    summary="",
)
async def get_trade(
    trade_id: str,
):
    mongodb = MongoDBCrud()
    result = mongodb.get_trade(trade_id=trade_id)

    return JSONResponse(
        content=result,
        status_code=status.HTTP_200_OK,
    )


@router.get(
    path="/all_trades",
    summary="",
    response_class=JSONResponse,
)
async def get_all_trades():
    mongodb = MongoDBCrud()
    result: list[dict] = mongodb.get_all_trades()

    return JSONResponse(
        content=result,
        status_code=status.HTTP_200_OK,
    )


@router.delete(
    path="/trade/{trade_id}",
    summary="",
)
async def delete_trade(
    trade_id: str,
):
    mongodb = MongoDBCrud()
    result = mongodb.remove_trade(trade_id=trade_id)

    return JSONResponse(
        content={
            "detail": "Trade correctly deleted",
            "result": result,
        },
        status_code=status.HTTP_200_OK,
    )
