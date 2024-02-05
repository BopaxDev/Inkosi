import random
import string
from dataclasses import asdict
from hashlib import sha256
from typing import Any

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from inkosi.database.postgresql.database import PostgreSQLCrud
from inkosi.database.postgresql.models import Authentication, Funds
from inkosi.database.postgresql.schemas import (
    FundInformation,
    LoginCredentials,
    RaiseNewFund,
    UserRole,
)
from inkosi.log.log import Logger
from inkosi.mailing.mailer import Mailer
from inkosi.mailing.schemas import EmailReceivedAdministratorFundRaising

router = APIRouter()

logger = Logger(
    module_name="Profile",
    package_name="api",
)


@router.get(
    path="/login",
    summary="",
)
async def login(
    credentials: LoginCredentials,
    request: Request,
) -> JSONResponse:
    postgresql = PostgreSQLCrud()
    records = postgresql.get_users(
        email_address=credentials.email_address,
        password=credentials.password,
    )

    match len(records):
        case 0:
            logger.warn(
                message=(
                    "Unable to locate the user with the following E-mail Address:"
                    f" {credentials.email_address}"
                )
            )

            return JSONResponse(
                content={
                    "detail": (
                        "Unable to locate the user through the E-mail Address given"
                    )
                },
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        case 1:
            if not UserRole.has(key=records[0].role):
                logger.warn(
                    message=(
                        "Unable to identify the role of user with the following ID and"
                        f" E-mail Address respectively: {records[0].id} and"
                        f" {records[0].email_address}"
                    )
                )
                return JSONResponse(
                    content={
                        "detail": "Unable to identify the role",
                    },
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            token_id: str = sha256(
                "".join(
                    [
                        random.choice(
                            list(set(string.ascii_uppercase).union(string.digits))
                        )
                        for _ in range(16)
                    ]
                ).encode()
            ).hexdigest()

            authentication = Authentication(
                id=token_id,
                user_type=records[0].role,
                user_id=records[0].id,
                ip_address=request.client.host,
                mode="webapp",
            )

            postgresql.postgresql_instance.add(model=[authentication])

            return JSONResponse(
                content={
                    "detail": "Successfully logged in",
                    "role": records[0].role,
                    "policies": records[0].policies,
                    "token": token_id,
                    "id": records[0].id,
                },
                status_code=status.HTTP_200_OK,
            )
        case 2:
            roles = set([user.get("Role", "") for user in records])
            if "" in roles:
                return JSONResponse(
                    content={"detail": "The Key selected is not correct"},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if len(roles) == 1:
                return JSONResponse(
                    content={
                        "detail": (
                            "Two users have been identified using the same E-mail"
                            " Address"
                        ),
                    },
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return JSONResponse(
                content={
                    "detail": (
                        "The user have been identified with two different type of roles"
                    )
                },
                status_code=status.HTTP_200_OK,
            )
        case _:
            logger.critical(
                message=(
                    "More than two users have been found with the following E-mail"
                    f" Address: {credentials.email_address}"
                )
            )
            return JSONResponse(
                content={
                    "detail": (
                        "More than two users have been found with the E-mail Address"
                        " given"
                    )
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@router.post(
    path="/fund",
    summary="",
)
async def raise_fund(
    raise_new_fund: RaiseNewFund,
) -> JSONResponse:
    postgresql = PostgreSQLCrud()

    fund = Funds(**asdict(raise_new_fund))
    result = postgresql.postgresql_instance.add(model=[fund])
    if result:
        mailer = Mailer()
        result: EmailReceivedAdministratorFundRaising = (
            mailer.send_email_to_administrator_for_fund_raising(
                raise_new_fund,
            )
        )

        return JSONResponse(
            content={
                "detail": (
                    "New Fund correctly raised. Corresponding record added to the"
                    " database."
                ),
            }
        )
    else:
        return JSONResponse(
            content={
                "detail": f"Unable to create the new fund: {raise_new_fund.fund_name}"
            },
            status_code=status.HTTP_200_OK,
        )


@router.get(
    path="/fund",
    summary="",
)
async def fund_information(
    fund_name: str,
) -> JSONResponse:
    # Check for policies through the Token given

    postgresql = PostgreSQLCrud()
    records: list[FundInformation] = postgresql.get_fund_information(
        fund_name=fund_name,
    )

    match len(records):
        case 0:
            return JSONResponse(
                content={
                    "detail": "Unable to fetch information regarding the specified fund"
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )
        case 1:
            record: dict[str, Any] = asdict(records[0])
            record["created_at"] = record.get("created_at").isoformat()

            return JSONResponse(
                content={
                    "detail": "Fund information correctly fetched",
                    "result": record,
                },
                status_code=status.HTTP_200_OK,
            )
        case _:
            return JSONResponse(
                content={
                    "detail": (
                        "Unable to correctly fetch the information two or more records"
                        " have been found."
                    ),
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
