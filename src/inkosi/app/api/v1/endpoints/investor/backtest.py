from fastapi import APIRouter

router = APIRouter()


@router.post(path="/backtest")
async def backtest():
    ...
