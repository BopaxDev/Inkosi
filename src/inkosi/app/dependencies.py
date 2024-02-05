from fastapi import Header, Request, status
from fastapi.exceptions import HTTPException

from inkosi.database.postgresql.database import PostgreSQLCrud
from inkosi.utils.settings import get_allowed_ip_addresses, get_api_settings


async def network_policies_check(
    request: Request,
) -> None:
    if (
        isinstance(get_allowed_ip_addresses(), str)
        and get_allowed_ip_addresses() == "*"
    ):
        return
    elif isinstance(get_allowed_ip_addresses(), list):
        ip_addr = request.client.host

        if ip_addr in get_allowed_ip_addresses():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your IP Address is not allowed to access the content",
            )


async def authentication(
    request: Request,
    x_token: str = Header(
        "",
    ),
) -> None:
    if not get_api_settings().TokenAuthentication:
        return

    if not x_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No data authentication have been provided",
        )

    postgres = PostgreSQLCrud()
    result = postgres.valid_authentication(
        x_token,
        request.client.host,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unable to authenticate through the token given",
        )
