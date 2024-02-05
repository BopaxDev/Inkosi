import random
from datetime import date, datetime
from functools import lru_cache

from sqlalchemy import ARRAY, Boolean, Column, Date, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from inkosi.database.postgresql.database import PostgreSQLInstance
from inkosi.database.postgresql.schemas import Tables


@lru_cache
def get_instance() -> PostgreSQLInstance:
    """
    Function to get an instance of the PostgreSQL database.

    Returns:
        PostgreSQLInstance: An instance of the PostgreSQLInstance class.
    """

    return PostgreSQLInstance()


class Administrators(get_instance().base):
    """
    SQLAlchemy model for the 'administrators' table.

    Attributes:
        id (int): Administrator ID.
        first_name (str): First name of the administrator.
        second_name (str): Second name of the administrator.
        email_address (str): Email address of the administrator (unique).
        birthday (date): Birthday of the administrator.
        fiscal_code (str): Fiscal code of the administrator.
        password (str): Password of the administrator.
        policies (list): List of policies associated with the administrator.
        active (bool): Indicates whether the administrator is active.
    """

    __tablename__ = Tables.ADMINISTRATOR

    id: int = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        default=lambda _: random.randint(10000000, 49999999),
    )
    first_name: str = Column(String, nullable=False)
    second_name: str = Column(String, nullable=False)
    email_address: str = Column(String, nullable=False, unique=True)
    birthday: date = Column(Date, nullable=True)
    fiscal_code: str = Column(String, nullable=True)
    password: str = Column(String, nullable=False)
    policies: list = Column(ARRAY(String), default=[])
    active: bool = Column(Boolean, default=True)


class Investors(get_instance().base):
    """
    SQLAlchemy model for the 'investors' table.

    Attributes:
        id (int): Investor ID.
        first_name (str): First name of the investor.
        second_name (str): Second name of the investor.
        email_address (str): Email address of the investor (unique).
        birthday (date): Birthday of the investor.
        fiscal_code (str): Fiscal code of the investor.
        password (str): Password of the investor.
        policies (list): List of policies associated with the investor.
        active (bool): Indicates whether the investor is active.
    """

    __tablename__ = Tables.INVESTOR

    id: int = Column(
        Integer,
        primary_key=True,
        index=True,
        default=lambda _: random.randint(50000000, 99999999),
    )
    first_name: str = Column(String, nullable=False)
    second_name: str = Column(String, nullable=False)
    email_address: str = Column(String, unique=True, nullable=False)
    birthday: date = Column(Date, nullable=True)
    fiscal_code: str = Column(String, nullable=True)
    password: str = Column(String, nullable=False)
    policies: list = Column(ARRAY(String), default=[])
    active: bool = Column(Boolean, default=True)


class Funds(get_instance().base):
    """
    SQLAlchemy model for the 'funds' table.

    Attributes:
        id (int): Fund ID.
        fund_name (str): Name of the fund (unique).
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

    __tablename__ = Tables.FUNDS

    id: int = Column(
        Integer,
        primary_key=True,
        index=True,
        default=lambda _: random.randint(10000000, 99999999),
    )
    fund_name: str = Column(String, nullable=False, unique=True)
    investment_firm: str = Column(String, nullable=True)
    created_at: date = Column(Date, nullable=False)
    administrators: list[int] = Column(ARRAY(Integer), default=[])
    investors: list[int] = Column(ARRAY(Integer), default=[])
    capital_distribution: dict = Column(JSONB, default={})
    commission_type: str = Column(String, default="percentual")
    commission_value: float = Column(Float, default=0.0)
    risk_limits: bool = Column(Boolean, default=False)
    raising_funds: bool = Column(Boolean, default=True)


class Authentication(get_instance().base):
    """
    SQLAlchemy model for the 'authentication' table.

    Attributes:
        id (str): Authentication ID.
        created_at (datetime): Date and time of authentication creation.
        validity (bool): Indicates the validity of the authentication.
        user_type (str): Type of user associated with the authentication.
        user_id (int): User ID associated with the authentication.
        mode (str): Authentication mode.
        ip_address (str): IP address associated with the authentication.
    """

    __tablename__ = Tables.AUTHENTICATION

    id: int = Column(
        String,
        primary_key=True,
        index=True,
        nullable=False,
    )

    created_at: datetime = Column(
        DateTime,
        default=lambda _: datetime.now(),
        nullable=False,
    )
    validity: bool = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    user_type: str = Column(String, nullable=False)
    user_id: int = Column(Integer, nullable=False)
    mode: str = Column(String, nullable=False)
    ip_address: str = Column(String, nullable=True)


class Strategies(get_instance().base):
    """
    SQLAlchemy model for the 'strategies' table.

    Attributes:
        id (str): Strategy ID.
        name (str): Name of the strategy.
        created_at (datetime): Date and time of strategy creation.
        administrator_id (int): ID of the administrator associated with the strategy.
        fund_names (list[str]): List of fund names associated with the strategy.
        category (str): Category of the strategy.
    """

    __tablename__ = Tables.STRATEGIES

    id: str = Column(
        String,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str = Column(String, nullable=True)
    created_at: datetime = Column(DateTime, nullable=False)
    administrator_id: int = Column(Integer, nullable=True)
    fund_names: list[str] = Column(ARRAY(String), default=[])
    category: str = Column(String, nullable=True)
