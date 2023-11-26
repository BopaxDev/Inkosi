from hashlib import sha256

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from inkosi import __project_name__, __version__
from inkosi.app import _constants
from inkosi.app.api.v1._routes import v1_router
from inkosi.database.mongodb.database import MongoDBInstance
from inkosi.database.postgresql.database import PostgreSQLInstance
from inkosi.database.postgresql.models import Administrator, Investor, get_instance
from inkosi.log.log import Logger
from inkosi.portfolio.risk_management import RiskManagement
from inkosi.utils.settings import get_default_administrators, get_default_investors

_API_HEALTHCHECK = "OK"
_API_DESCRIPTION = "Inkosi API"
_API_STATUS = "active"

logger = Logger(
    module_name="Main",
    package_name="app",
)

app = FastAPI(
    title=_constants.APPLICATION_NAME,
)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    v1_router,
    prefix=_constants.API + _constants.V1,
)


@app.on_event(
    event_type="startup",
)
async def startup_event() -> None:
    mongo_manager = MongoDBInstance()
    if not mongo_manager.is_connected():
        logger.error(message="Unable to connect to the MongoDB Instance")

    get_instance().connect()

    RiskManagement()

    postgres_instance = PostgreSQLInstance()

    for investor in get_default_investors():
        postgres_instance.add(
            model=[
                Investor(
                    first_name=investor.first_name,
                    second_name=investor.second_name,
                    email_address=investor.email_address,
                    birthday=investor.birthday,
                    fiscal_code=investor.fiscal_code,
                    password=sha256(investor.password.encode()).hexdigest(),
                    policies=investor.policies,
                    active=investor.active,
                )
            ]
        )

    for administrator_id, administrator in get_default_administrators().items():
        postgres_instance.add(
            model=[
                Administrator(
                    id=administrator_id,
                    first_name=administrator.first_name,
                    second_name=administrator.second_name,
                    email_address=administrator.email_address,
                    birthday=administrator.birthday,
                    fiscal_code=administrator.fiscal_code,
                    password=sha256(administrator.password.encode()).hexdigest(),
                    policies=administrator.policies,
                    active=administrator.active,
                )
            ]
        )


@app.on_event(
    event_type="shutdown",
)
async def shutdown() -> None:
    RiskManagement().unload_model()


@app.get(
    path=_constants.HEALTHCHECK,
    summary=f"Get the healthcheck of {_constants.APPLICATION_NAME}",
    status_code=status.HTTP_200_OK,
    response_model=str,
)
async def healthcheck() -> str:
    """
    Get the healthcheck of the application

    Returns
    -------
    str
        A message to ensure that the application is active
    """

    return _API_HEALTHCHECK


@app.get(
    path=_constants.STATUS,
    summary=f"Get the status of {_constants.APPLICATION_NAME}",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],
)
async def status() -> dict[str, str]:
    """
    Get the status of the application

    Returns
    -------
    dict[str, str]
        A dictionary containing metadata about the status of the application
    """

    return {
        "name": __project_name__,
        "version": __version__,
        "description": _API_DESCRIPTION,
        "status": _API_STATUS,
    }
