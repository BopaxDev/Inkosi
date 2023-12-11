from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from inkosi.database.postgresql.database import PostgreSQLCrud
from inkosi.database.postgresql.schemas import DepositFundRequest, FundInformation

router = APIRouter()


@router.post(
    path="/deposit_fund",
    summary="",
)
async def deposit_fund(
    deposit_fund_request: DepositFundRequest,
) -> JSONResponse:
    postgres = PostgreSQLCrud()

    funds_information: list[FundInformation] = postgres.get_fund_information(
        deposit_fund_request.fund_name
    )

    if len(funds_information) == 0:
        return JSONResponse(
            content={
                "detail": "Unable to recognise the fund through the provided name"
            },
            status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
        )
    elif len(funds_information) > 1:
        return JSONResponse(
            content={
                "detail": "More or two funds have been found with the same name",
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if not funds_information[0].raising_funds:
        return JSONResponse(
            content={
                "detail": (
                    "You are not currently authorised to deposit fund over a conclused"
                    " fund raising phase"
                )
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if not postgres.check_for_investor_existence(deposit_fund_request.investor_id):
        return JSONResponse(
            content={
                "detail": "Unable to recognise the investor through the provided ID",
            },
            status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
        )

    result = postgres.deposit_fund(
        fund_name=deposit_fund_request.fund_name,
        investor_id=deposit_fund_request.investor_id,
        amount=deposit_fund_request.deposit,
    )

    return JSONResponse(
        content={
            "detail": "Deposit Fund Operation",
            "result": result,
        },
        status_code=status.HTTP_200_OK,
    )
