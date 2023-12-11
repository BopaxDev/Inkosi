from fastapi import APIRouter, Depends

from inkosi.app import _constants
from inkosi.app.api.v1.endpoints.admin.administration import (
    router as administration_router,
)
from inkosi.app.api.v1.endpoints.admin.operations import router as operations_router
from inkosi.app.api.v1.endpoints.admin.scheduler import router as scheduler_router
from inkosi.app.api.v1.endpoints.admin.trades.database import (
    router as database_trading_router,
)
from inkosi.app.api.v1.endpoints.admin.trades.trading import router as trading_router
from inkosi.app.api.v1.endpoints.investor.administration import (
    router as investor_administration_router,
)
from inkosi.app.api.v1.endpoints.investor.backtest import (
    router as investor_backtest_router,
)
from inkosi.app.api.v1.endpoints.investor.operations import (
    router as investor_operations_router,
)
from inkosi.app.api.v1.endpoints.profile import router as profile_router
from inkosi.app.dependencies import authentication, network_policies_check

v1_router = APIRouter()

v1_router.include_router(
    router=administration_router,
    tags=["Administrator"],
    dependencies=[
        # Depends(authentication),
        Depends(network_policies_check),
    ],
)
v1_router.include_router(
    router=operations_router,
    tags=["Administrator Operations"],
    dependencies=[
        Depends(authentication),
        Depends(network_policies_check),
    ],
)
v1_router.include_router(
    router=scheduler_router,
    tags=["Scheduler"],
)
v1_router.include_router(
    router=database_trading_router,
    prefix=_constants.v1.DATABASE,
    tags=["Database Trades Operations"],
)
v1_router.include_router(
    router=trading_router,
    tags=["Trading"],
)

v1_router.include_router(
    router=investor_operations_router,
    tags=["Investor Operations"],
)
v1_router.include_router(
    router=investor_administration_router,
    tags=["Investor Administration"],
)
v1_router.include_router(
    router=investor_backtest_router,
    tags=["Investor Backtest"],
)

v1_router.include_router(
    router=profile_router,
    tags=["Profile"],
)
