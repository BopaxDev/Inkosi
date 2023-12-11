import random
import string
from hashlib import sha256

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from inkosi.app.schemas import Mode
from inkosi.database.postgresql.database import PostgreSQLCrud
from inkosi.database.postgresql.models import Authentication

router = APIRouter()


@router.post(
    path="/generate_token_backtest",
    summary="",
)
async def generate_token_backtest(
    request: Request,
) -> JSONResponse:
    postgresql = PostgreSQLCrud()

    token_id: str = sha256(
        "".join(
            [
                random.choice(list(set(string.ascii_uppercase).union(string.digits)))
                for _ in range(16)
            ]
        ).encode()
    ).hexdigest()

    authentication = Authentication(
        id=token_id,
        ip_address=request.client.host,
        mode=Mode.BACKTEST,
    )

    postgresql.postgresql_instance.add(model=[authentication])
