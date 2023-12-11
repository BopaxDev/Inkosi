from dataclasses import dataclass, field
from datetime import date, datetime

from inkosi.utils.utils import CommissionTypes, EnhancedStrEnum


class Tables(EnhancedStrEnum):
    """
    Enumeration class representing different tables in a database.

    Attributes:
        ADMINISTRATOR (str): Table for administrators.
        INVESTOR (str): Table for investors.
        FUNDS (str): Table for funds.
        AUTHENTICATION (str): Table for authentication.
        STRATEGIES (str): Table for strategies.
    """

    ADMINISTRATOR: str = "administrators"
    INVESTOR: str = "investors"
    FUNDS: str = "funds"
    AUTHENTICATION: str = "authentication"
    STRATEGIES: str = "strategies"


class UserRole(EnhancedStrEnum):
    """
    Enumeration class representing user roles.

    Attributes:
        ADMINISTRATOR (str): Administrator role.
        INVESTOR (str): Investor role.
    """

    ADMINISTRATOR: str = "administrator"
    INVESTOR: str = "investor"


class CategoriesATS(EnhancedStrEnum):
    """
    Enumeration class representing categories in an Automated Trading System (ATS).

    Attributes:
        GENERAL_PURPOSE (str): General-purpose category.
        TECHNICAL (str): Technical indicators category.
    """

    GENERAL_PURPOSE: str = "general_purpose"
    TECHNICAL: str = "technical_indicators"


@dataclass
class PoliciesUpdate:
    """
    Data class representing an update to user policies.

    Attributes:
        user_id (int): User ID.
        role (str): User role.
        policies (list[str] | str): List of policies or a single policy.
    """

    user_id: int
    role: str
    policies: list[str] | str


@dataclass
class User:
    """
    Data class representing a user.

    Attributes:
        id (int): User ID.
        full_name (str): Full name of the user.
        first_name (str): First name of the user.
        second_name (str): Second name of the user.
        email_address (str): Email address of the user.
        role (str): User role.
        policies (list[str]): List of user policies.
    """

    id: int
    full_name: str
    first_name: str
    second_name: str
    email_address: str
    role: str
    policies: list[str]


@dataclass
class AdministratorProfile:
    """
    Data class representing an administrator's profile.

    Attributes:
        id (int): Administrator's ID.
        full_name (str): Full name of the administrator.
        first_name (str): First name of the administrator.
        second_name (str): Second name of the administrator.
        email_address (str): Email address of the administrator.
        policies (list[str]): List of administrator policies.
        role (str): Administrator role.
    """

    id: int
    full_name: str
    first_name: str
    second_name: str
    email_address: str
    policies: list[str]
    role: str


@dataclass
class InvestorProfile:
    """
    Data class representing an investor's profile.

    Attributes:
        id (int): Investor's ID.
        full_name (str): Full name of the investor.
        first_name (str): First name of the investor.
        second_name (str): Second name of the investor.
        email_address (str): Email address of the investor.
        policies (list[str]): List of investor policies.
        role (str): Investor role.
    """

    id: int
    full_name: str
    first_name: str
    second_name: str
    email_address: str
    policies: list[str]
    role: str


@dataclass
class ATSProfile:
    """
    Data class representing an Automated Trading System (ATS) profile.

    Attributes:
        id (int): ATS ID.
        full_name (str): Full name of the ATS.
        administrator_id (int): ID of the administrator associated with the ATS.
        fund_names (list): List of fund names associated with the ATS.
        category (str): Category of the ATS.
    """

    id: int
    full_name: str
    administrator_id: int
    fund_names: list
    category: str


@dataclass
class Fund:
    """
    Data class representing a fund.

    Attributes:
        id (int): Fund ID.
        fund_name (str): Name of the fund.
        investment_firm (str): Name of the investment firm.
        created_at (date): Date of fund creation.
        administrators (list[int]): List of administrator IDs associated with the fund.
        investors (list[int]): List of investor IDs associated with the fund.
        capital_distribution (dict): Dictionary representing capital distribution.
        commission_type (str): Type of commission.
        commission_value (float): Value of the commission.
        risk_limits (bool): Indicates whether risk limits are applied.
        raising_funds (bool): Indicates whether the fund is currently raising funds.
    """

    id: int
    fund_name: str
    investment_firm: str
    created_at: date
    administrators: list[int]
    investors: list[int]
    capital_distribution: dict[str, float]
    commission_type: str
    commission_value: float
    risk_limits: bool
    raising_funds: bool


@dataclass
class AuthenticationOutput:
    """
    Data class representing the output of an authentication process.

    Attributes:
        id (str): Authentication ID.
        created_at (datetime): Date and time of authentication creation.
        validity (bool): Indicates the validity of the authentication.
        user_id (str): User ID associated with the authentication.
        ip_address (str): IP address associated with the authentication.
    """

    id: str
    created_at: datetime
    validity: bool
    user_id: str
    ip_address: str


@dataclass
class LoginCredentials:
    """
    Data class representing login credentials.

    Attributes:
        email_address (str): Email address used for login.
        password (str): Password associated with the account.
    """

    email_address: str
    password: str


@dataclass
class FundInformation:
    """
    Data class representing information about a fund.

    Attributes:
        id (int): Fund ID.
        fund_name (str): Name of the fund.
        created_at (date | str): Date of fund creation or a string representation.
        investment_firm (str | None): Name of the investment firm (optional).
        administrators (list[int]): List of administrator IDs associated with the fund.
        administrators_full_name (list[str]): List of full names of administrators
        associated with the fund.
        investors (list[int]): List of investor IDs associated with the fund.
        investors_full_name (list[str]): List of full names of investors associated with
        the fund.
        capital_distribution (dict): Dictionary representing capital distribution.
        commission_type (str): Type of commission.
        commission_value (float): Value of the commission.
        strategies (list[str] | str): List of strategies associated with the fund or a
        single strategy (optional).
        raising_funds (bool): Indicates whether the fund is currently raising funds.
    """

    id: int
    fund_name: str
    created_at: date | str
    investment_firm: str | None = None
    administrators: list[int] = field(default_factory=[])
    administrators_full_name: list[str] = field(default_factory=[])
    investors: list[int] = field(default_factory=[])
    investors_full_name: list[str] = field(default_factory=[])
    capital_distribution: dict = field(default_factory={})
    commission_type: str = field(default_factory=str)
    commission_value: float = field(default=0.0)
    strategies: list[str] | str = field(default_factory=[])
    raising_funds: bool = field(default=False)


@dataclass
class RaiseNewFund:
    """
    Data class representing information to raise a new fund.

    Attributes:
        fund_name (str): Name of the new fund.
        investment_firm (str | None): Name of the investment firm (optional).
        commission_type (CommissionTypes): Type of commission.
        commission_value (float): Value of the commission.
        administrators (list[int]): List of administrator IDs associated with the new
        fund.
        investors (list[str]): List of investor names associated with the new fund
        (optional).
        capital_distribution (dict): Dictionary representing initial capital
        distribution.
        created_at (date): Date of fund creation (default is the current date).
    """

    fund_name: str
    investment_firm: str | None
    commission_type: CommissionTypes
    commission_value: float
    administrators: list[int]
    investors: list[str] = field(default_factory=list)
    capital_distribution: dict = field(default_factory=dict)
    created_at: date = field(default=datetime.today())


@dataclass
class AddInvestorToFund:
    """
    Data class representing the request to add an investor to a fund.

    Attributes:
        investor_id (int | None): ID of the investor (optional).
        fund (str | int): Name or ID of the fund.
    """

    investor_id: int | None
    fund: str | int


@dataclass
class AddAdministratorToFund:
    """
    Data class representing the request to add an administrator to a fund.

    Attributes:
        administrator_id (int | None): ID of the administrator (optional).
        fund (str | int): Name or ID of the fund.
    """

    administrator_id: int | None
    fund: str | int


@dataclass
class Commission:
    """
    Data class representing commission details for a fund.

    Attributes:
        commission_type (str): Type of commission.
        commission_value (float | int): Value of the commission.
        fund (str | int): Name or ID of the fund.
    """

    commission_type: str
    commission_value: float | int
    fund: str | int


@dataclass
class DepositFundRequest:
    """
    Data class representing a deposit request for a fund.

    Attributes:
        investor_id (int): ID of the investor making the deposit.
        deposit (float): Amount to be deposited.
        fund_name (str): Name of the fund.
    """

    investor_id: int
    deposit: float
    fund_name: str
