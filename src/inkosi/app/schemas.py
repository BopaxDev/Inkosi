from dataclasses import dataclass
from datetime import date

from inkosi.utils.utils import EnhancedStrEnum


class Mode(EnhancedStrEnum):
    """
    Enumeration class for different operational modes.

    Attributes:
        BACKTEST (str): Backtesting mode.
        WEBAPP (str): Web application mode.
    """

    BACKTEST: str = "backtesting"
    WEBAPP: str = "webapp"


@dataclass
class AdministratorRequest:
    """
    Data class representing a request to create an administrator.

    Attributes:
        first_name (str): First name of the administrator.
        second_name (str): Second name of the administrator.
        email_address (str): Email address of the administrator.
        password (str): Password for the administrator.
        policies (list[str]): List of policies associated with the administrator.
        birthday (date | None): Birthday of the administrator (optional).
        fiscal_code (str | None): Fiscal code of the administrator (optional).
        active (bool): Flag indicating whether the administrator is active
            (default is True).
    """

    first_name: str
    second_name: str
    email_address: str
    password: str
    policies: list[str]
    birthday: date | None = None
    fiscal_code: str | None = None
    active: bool = True


@dataclass
class InvestorRequest:
    """
    Data class representing a request to create an investor.

    Attributes:
        first_name (str): First name of the investor.
        second_name (str): Second name of the investor.
        email_address (str): Email address of the investor.
        password (str): Password for the investor.
        policies (list[str]): List of policies associated with the investor.
        birthday (date | None): Birthday of the investor (optional).
        fiscal_code (str | None): Fiscal code of the investor (optional).
        active (bool): Flag indicating whether the investor is active (default is True).
    """

    first_name: str
    second_name: str
    email_address: str
    password: str
    policies: list[str]
    birthday: date | None = None
    fiscal_code: str | None = None
    active: bool = True


@dataclass
class StrategyRequest:
    """
    Data class representing a request to create a strategy.

    Attributes:
        id (str): Identifier for the strategy.
        administrator_id (int): ID of the administrator associated with the strategy.
        fund_name (str | None): Name of the fund associated with the strategy
            (optional).
        category (str): Category of the strategy.
        name (str | None): Name of the strategy (optional).
    """

    id: str
    administrator_id: int
    fund_name: str | None
    category: str
    name: str | None = None


@dataclass
class Returns:
    """
    Data class representing returns information.

    Attributes:
        balance (str): Balance information.
    """

    balance: str
