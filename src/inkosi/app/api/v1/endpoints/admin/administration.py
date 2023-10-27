from hashlib import sha256

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse

from inkosi.app.schemas import AdministratorRequest, Returns
from inkosi.database.postgresql.database import PostgreSQLCrud, PostgreSQLInstance
from inkosi.database.postgresql.models import Administrator
from inkosi.database.postgresql.schemas import (
    AdministratorProfile,
    Fund,
    PoliciesUpdate,
    ReturnRequest,
)

router = APIRouter()


@router.post(
    path="/create_administrator",
    response_model=list[AdministratorProfile],
)
def create_administrator(administrator_request: AdministratorRequest):
    postgres_instance = PostgreSQLInstance()

    administrator = Administrator(
        first_name=administrator_request.first_name,
        second_name=administrator_request.second_name,
        email_address=administrator_request.email_address,
        birthday=administrator_request.birthday,
        fiscal_code=administrator_request.fiscal_code,
        password=sha256(administrator_request.password.encode()).hexdigest(),
        policies=administrator_request.policies,
        active=administrator_request.active,
    )

    postgres_instance.add(model=[administrator])

    postgres = PostgreSQLCrud()
    return postgres.get_administrator_by_email_address(
        email_address=administrator.email_address
    )


@router.get(
    path="/list_portfolio_managers",
    response_model=list[AdministratorProfile],
)
def list_portfolio_managers(status: bool | None = None):
    """
    Return the list of Active, Inactive or all Portfolio Managers

    Parameters
    ----------
    status : bool | None, optional
        Specify if you would like to discover active or inactive portfolio managers
        , by default None

    Returns
    -------
    list[AdministratorProfile]
        List containing records of Portfolio Manager, each of them contains information
        such as: Full Name, E-mail Address, Policies, ...
    """
    postgresql = PostgreSQLCrud()

    if status is None:
        return postgresql.get_portfolio_managers()


@router.get(
    path="/list_funds",
    response_model=list[Fund],
)
def list_funds(status: bool | None = None):
    """
    Return the list of Active, Inactive or all Funds

    Parameters
    ----------
    status : bool | None, optional
        Specify if you would like to discover active or inactive funds, by default None

    Returns
    -------
    list[Fund]
        List containing records of Fund, each of them contains information
        such as: id, Fund Name, Portfolio Managers, ...
    """
    postgresql = PostgreSQLCrud()

    if status is None:
        return postgresql.get_funds()


@router.post(path="/returns", response_model=Returns)
def returns(return_request: ReturnRequest):
    ...


@router.put(
    path="/update_policies",
    response_class=Response,
)
def update_policies(policies_update: PoliciesUpdate):
    postgres = PostgreSQLCrud()
    result = postgres.update_policies(
        policies_update=policies_update,
    )

    if not result:
        return JSONResponse(
            content={
                "detail": "Unable to update the policy",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return JSONResponse(
        content={
            "detail": "Correctly updated",
        },
        status_code=status.HTTP_200_OK,
    )
