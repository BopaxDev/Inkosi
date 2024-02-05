from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache
from pathlib import Path

from omegaconf import OmegaConf
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    """
    Settings class for configuring MetaTrader 5 (MT5) account information.

    This class inherits from BaseSettings and includes configuration options for
    specifying the environment file, environment variable prefix, and case sensitivity
    for settings.

    Settings:
        ACCOUNT (int): MetaTrader 5 account number.
        PASSWORD (str): Password for the MetaTrader 5 account.
        SERVER (str): MetaTrader 5 server name.

    Note:
        The settings ACCOUNT, PASSWORD, and SERVER correspond to MetaTrader 5
        account information.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="INKOSI_",
        case_sensitive=False,
    )

    ACCOUNT: int
    PASSWORD: str
    SERVER: str


@dataclass
class TimeActivity:
    """
    Data class representing the maximum amount of time before the generated token for
    access expires.

    Attributes:
        days (int): Number of days until token expiration.
        hours (int): Number of hours until token expiration.
        minutes (int): Number of minutes until token expiration.
        seconds (int): Number of seconds until token expiration.

    Note:
        This class is designed to hold information about the time duration
        before an access token expires. It is commonly used in scenarios where
        access tokens have a limited validity period.
    """

    days: int
    hours: int
    minutes: int
    seconds: int


@dataclass
class MongoDBCollections:
    """
    Data class representing the MongoDB Collections used respectively for Logs and
    Trading Operations.
    """

    Log: str
    Trade: str


@dataclass
class PostgreSQL:
    """
    Data class representing the configuration details for connecting to a PostgreSQL
    database.

    Attributes:
        PROTOCOL (str): Protocol used for the connection (e.g., "postgresql").
        USERNAME (str): Username for authenticating the database connection.
        PASSWORD (str): Password for authenticating the database connection.
        HOSTNAME (str): Hostname or IP address of the PostgreSQL server.
        PORT (int): Port number on which the PostgreSQL server is listening.
        DATABASE (str): Name of the PostgreSQL database to connect to.
        SCHEMA (str): Name of the database schema to use.
        PARAMETERS (str): Additional connection parameters as a string.

    Note:
        This class is designed to hold the configuration details required for connecting
        to a PostgreSQL database. It includes information such as the protocol,
        username, password, hostname, port, database name, schema, and additional
        parameters.
    """

    PROTOCOL: str
    USERNAME: str
    PASSWORD: str
    HOSTNAME: str
    PORT: int
    DATABASE: str
    SCHEMA: str
    PARAMETERS: str


@dataclass
class MongoDB:
    """
    Data class representing the configuration details for connecting to a MongoDB
    database.

    Attributes:
        PROTOCOL (str): Protocol used for the connection (e.g., "mongodb" or
        "mongodb+srv").
        USERNAME (str): Username for authenticating the MongoDB connection.
        PASSWORD (str): Password for authenticating the MongoDB connection.
        HOSTNAME (str): Hostname or IP address of the MongoDB server.
        PORT (int): Port number on which the MongoDB server is listening.
        DATABASE (str): Name of the MongoDB database to connect to.
        PARAMETERS (str): Additional connection parameters as a string.
        TLS (bool): Flag indicating whether to use TLS/SSL for the connection.

        COLLECTIONS (MongoDBCollections): An instance of the MongoDBCollections class,
            representing the collections within the MongoDB database.

    Note:
        This class is designed to hold the configuration details required for connecting
        to a MongoDB database. It includes information such as the protocol, username,
        password, hostname, port, database name, parameters, TLS usage, and collections.
    """

    PROTOCOL: str
    USERNAME: str
    PASSWORD: str
    HOSTNAME: str
    PORT: int
    DATABASE: str
    PARAMETERS: str
    TLS: bool

    COLLECTIONS: MongoDBCollections


@dataclass
class API:
    """
    Data class representing the configuration details for an API.

    Attributes:
        AllowedIPAddresses (str | list): Allowed IP addresses for API access.
            This can be a single IP address (string) or a list of IP addresses.

        TokenAuthentication (bool): Flag indicating whether token authentication is
        required.

        IPAddressCorrespondence (bool): Flag indicating whether IP address
        correspondence is checked.

        TimeActivity (TimeActivity): An instance of the TimeActivity class representing
            the maximum amount of time before the generated token for access expires.

        APIs (List): List of APIs associated with the configuration.

    Note:
        This class is designed to hold the configuration details for an API. It includes
        information such as allowed IP addresses, token authentication, IP address
        correspondence, time activity settings, and a list of associated APIs.
    """

    AllowedIPAddresses: str | list
    TokenAuthentication: bool
    IPAddressCorrespondence: bool
    TimeActivity: TimeActivity
    APIs: list


@dataclass
class Policies:
    """
    Data class representing access policies for different user roles.

    Attributes:
        Administrator (list[str]): List of policies for users with the Administrator
        role. Investor (list[str]): List of policies for users with the Investor role.

    Note:
        This class is designed to hold access policies for different user roles.
        It includes lists of policies for Administrators and Investors.
    """

    Administrator: list[str]
    Investor: list[str]


@dataclass
class RiskManagement:
    """
    Data class representing risk management configuration.

    Attributes:
        Models (list | None): List of risk management models.
            If None, no specific risk management models are defined.

    Note:
        This class is designed to hold the configuration for risk management.
        It includes a list of risk management models, which can be None if no
        specific models are defined.
    """

    Models: list | None


@dataclass
class TechnicalIndicators:
    """
    Data class representing configuration for technical indicators.

    Attributes:
        MovingAveragePeriod (int | float): Period for the moving average.
            This can be an integer or a float value.

    Note:
        This class is designed to hold the configuration for technical indicators.
        It includes the period for the moving average, which can be either an integer
        or a float value.
    """

    MovingAveragePeriod: int | float


@dataclass
class Backtesting:
    """
    Data class representing backtesting settings.

    Attributes:
        Tickers (list): List of tickers for backtesting.
    """

    Tickers: list[str]


@dataclass
class TradingRiskManagement:
    """
    Data class representing backtesting settings.
    These essentially represents the value used as default when no pre-trained risk
    management model has been loaded.

    Attributes:
        TakeProfit (int | float): Value indicating the take profit
        StopLoss (int | float): Value indicating the stop loss
    """

    Volume: int | float = field(default=0.0)
    TakeProfit: int | float = field(default=0.0)
    StopLoss: int | float = field(default=0.0)


@dataclass
class Settings:
    """
    Data class representing system settings.

    Attributes:
        PostgreSQL (PostgreSQL): PostgreSQL settings.
        MongoDB (MongoDB): MongoDB settings.
        API (API): API settings.
        Policies (Policies): Policies settings.
        RiskManagement (RiskManagement): Risk management settings.
        TechnicalIndicators (TechnicalIndicators): Technical indicators settings.
        Backtesting (Backtesting): Backtesting settings.
        TradingTickers (list): List of trading tickers.

    Optional Attributes:
        TradingRiskManagement (TradingRiskManagement): Default Risk Management Values
        DefaultAdministrators (dict): Default administrators' information.
        DefaultInvestors (list): Default investors' information.
        DefaultFunds (dict): Default funds' information.
        DefaultStrategies (list): Default strategies' information.
    """

    PostgreSQL: PostgreSQL
    MongoDB: MongoDB
    API: API
    Policies: Policies
    RiskManagement: RiskManagement
    TechnicalIndicators: TechnicalIndicators
    Backtesting: Backtesting
    TradingTickers: list
    TradingRiskManagement: TradingRiskManagement

    DefaultAdministrators: dict[int, dict[str, str | date | list | None]] = field(
        default_factory=dict
    )
    DefaultInvestors: list[dict[str, str | date | list | None]] = field(
        default_factory=list
    )

    DefaultFunds: dict[int, dict[str, str | date | list | None]] = field(
        default_factory=dict
    )
    DefaultStrategies: list[dict[str, str | date | list | None]] = field(
        default_factory=list
    )


@lru_cache
def get_environmental_settings() -> EnvSettings:
    """
    Function to retrieve environmental settings using caching.

    Returns:
        EnvSettings: An instance of the EnvSettings class representing
            the environmental configuration settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result
    """

    return EnvSettings()


@lru_cache
def get_settings() -> Settings:
    """
    Function to fetch application settings using caching.

    Returns:
        Settings: An instance of the Settings class representing the overall
            configuration settings for the application.
    """

    settings_import = OmegaConf.load(
        Path(__file__)
        .absolute()
        .parent.parent.parent.parent.joinpath(
            "config.yaml",
        ),
    )

    return OmegaConf.structured(
        Settings(**settings_import),
    )


@lru_cache
def get_postgresql_settings() -> PostgreSQL:
    """
    Function to fetch PostgreSQL settings using caching.

    Returns:
        PostgreSQL: An instance of the PostgreSQL class representing the overall
            configuration settings for the PostgreSQL Instance.
    """

    return get_settings().PostgreSQL


@lru_cache
def get_postgresql_schema() -> str:
    """
    Get the PostgreSQL schema from the configuration settings.

    Returns:
        str: The PostgreSQL schema obtained from the configuration settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves the PostgreSQL schema from the configuration settings
        using `get_postgresql_settings()`. It then returns the obtained schema as a
        string.
    """

    return get_postgresql_settings().SCHEMA


@lru_cache
def get_postgresql_url() -> str:
    """
    Get the PostgreSQL connection URL from the configuration settings.

    Returns:
        str: The PostgreSQL connection URL constructed from the configuration settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves PostgreSQL configuration settings from the overall
        application settings using `get_settings()`. It then constructs the PostgreSQL
        connection URL by combining the protocol, username, password, hostname, port,
        and database information from the configuration settings.

        Returns the constructed PostgreSQL connection URL as a string.
    """

    postgresql_settings: PostgreSQL = get_settings().PostgreSQL

    return (
        f"{postgresql_settings.PROTOCOL}://"
        f"{postgresql_settings.USERNAME}:"
        f"{postgresql_settings.PASSWORD}@"
        f"{postgresql_settings.HOSTNAME}:"
        f"{postgresql_settings.PORT}/{postgresql_settings.DATABASE}"
    )


@lru_cache
def get_mongodb_settings() -> MongoDB:
    """
    Get the MongoDB configuration settings.

    Returns:
        MongoDB: An instance of the MongoDB configuration settings obtained from the
            overall application settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.
    """

    return get_settings().MongoDB


@lru_cache
def get_mongodb_collection() -> MongoDBCollections:
    """
    Retrieve the MongoDB collection from the application settings.

    Returns:
        MongoDBCollections: An instance of the MongoDBCollections class representing
            the MongoDB collection.
    """

    return get_mongodb_settings().COLLECTIONS


@lru_cache
def get_mongodb_url(no_port: bool = False) -> str:
    """
    Get the MongoDB connection URL from the configuration settings.

    Returns:
        str: The MongoDB connection URL constructed from the configuration settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves MongoDB configuration settings from the overall
        application settings using `get_settings()`. It then constructs the MongoDB
        connection URL by combining the protocol, username, password, hostname, port,
        and parameters information from the configuration settings.

        Returns the constructed MongoDB connection URL as a string.
    """

    mongodb_settings = get_settings().MongoDB

    return (
        f"{mongodb_settings.PROTOCOL}://"
        f"{mongodb_settings.USERNAME}:"
        f"{mongodb_settings.PASSWORD}@"
        f"{mongodb_settings.HOSTNAME}"
        f"{':' + str(mongodb_settings.PORT) if not no_port else ''}/"
        f"{mongodb_settings.PARAMETERS}"
    )


@lru_cache
def get_api_settings() -> API:
    """
    Get the API configuration settings.

    Returns:
        API: An instance of the API configuration settings obtained from the overall
            application settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves API configuration settings from the overall
        application settings using `get_settings()`.

        Returns an instance of the API configuration settings.
    """

    return get_settings().API


@lru_cache
def get_allowed_ip_addresses() -> list | str:
    """
    Get the allowed IP addresses from the API configuration.

    Returns:
        list | str: A list of allowed IP addresses or a string specifying IP address
            correspondence, obtained from the API configuration.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves the allowed IP addresses from the API configuration
        using `get_api_settings()`.

        Returns a list of allowed IP addresses or a string specifying IP address
        correspondence.
    """

    return get_api_settings().AllowedIPAddresses


@lru_cache
def get_ip_address_correspondence() -> bool:
    """
    Get the IP address correspondence setting from the API configuration.

    Returns:
        bool: True if IP address correspondence is enabled, False otherwise.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves the IP address correspondence setting from the API
        configuration using `get_api_settings()`.

        Returns True if IP address correspondence is enabled, and False otherwise.
    """

    return get_api_settings().IPAddressCorrespondence


@lru_cache
def get_time_activity() -> dict:
    """
    Get the time activity configuration from the API settings.

    Returns:
        dict: A dictionary containing time activity configuration obtained from the API
            settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves time activity configuration from the API settings
        using `get_api_settings()`.

        Returns a dictionary containing time activity configuration.
    """

    return get_api_settings().TimeActivity


@lru_cache
def get_administrators_policies() -> list:
    """
    Get the policies for administrators.

    Returns:
        list: A list of policies for administrators obtained from the overall
            application settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves policies for administrators from the overall application
        settings using `get_settings()`.

        Returns a list of policies for administrators.
    """

    return get_settings().Policies.Administrator


@lru_cache
def get_investors_policies() -> list:
    """
    Get the policies for investors.

    Returns:
        list: A list of policies for investors obtained from the overall application
            settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves policies for investors from the overall application
        settings using `get_settings()`.

        Returns a list of policies for investors.
    """

    return get_settings().Policies.Investor


@lru_cache
def get_risk_management() -> RiskManagement:
    """
    Get the risk management configuration settings.

    Returns:
        RiskManagement: An instance of the risk management configuration settings
            obtained from the overall application settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves risk management configuration settings from the overall
        application settings using `get_settings()`.

        Returns an instance of the risk management configuration settings.
    """

    return get_settings().RiskManagement


@lru_cache
def get_risk_management_models() -> list | None:
    """
    Get the risk management models.

    Returns:
        list | None: A list of risk management models obtained from the overall
            application settings, or None if no models are specified.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves risk management models from the overall application
        settings using `get_risk_management()`.

        Returns a list of risk management models or None if no models are specified.
    """

    return get_risk_management().Models


@lru_cache
def get_technical_indicators_values() -> TechnicalIndicators:
    """
    Get the configuration values for technical indicators.

    Returns:
        TechnicalIndicators: An instance of the technical indicators configuration
            settings obtained from the overall application settings.

    Note:
        This function is decorated with the LRU (Least Recently Used) cache,
        which helps in caching the result of the function to improve performance.

        The function retrieves technical indicators configuration settings from the
        overall application settings using `get_settings()`.

        Returns an instance of the technical indicators configuration settings.
    """

    return get_settings().TechnicalIndicators


@lru_cache
def get_default_administrators() -> dict[int, dict[str, str | date | list | None]]:
    """
    Retrieve the default administrators from the application settings.

    Returns:
        dict[int, dict[str, Union[str, date, list, None]]]: A dictionary containing
            default administrators. The keys are integers representing administrator
            IDs, and the values are dictionaries with keys representing administrator
            attributes.
            Possible attributes include:
            - 'name' (str): The name of the administrator.
            - 'birth_date' (date): The birth date of the administrator.
            - 'permissions' (list): A list of permissions granted to the administrator.
            - Other custom attributes, which may be None.
    """

    return get_settings().DefaultAdministrators


@lru_cache
def get_default_investors() -> list[dict[str, str | date | list | None]]:
    """
    Retrieve the default investors from the application settings.

    Returns:
        list[dict[str, Union[str, date, list, None]]]: A list of dictionaries
            representing default investors. Each dictionary contains keys representing
            investor attributes. Possible attributes include:
            - 'name' (str): The name of the investor.
            - 'birth_date' (date): The birth date of the investor.
            - 'investments' (list): A list of investments made by the investor.
            - Other custom attributes, which may be None.
    """

    return get_settings().DefaultInvestors


@lru_cache
def get_default_funds() -> dict[int, dict[str, str | date | list | None]]:
    """
    Retrieve the default funds from the application settings.

    Returns:
        dict[int, dict[str, Union[str, date, List, None]]]: A dictionary containing
        default funds. The keys are integers representing fund IDs, and the values are
        dictionaries with keys representing fund attributes. Possible attributes
        include:
        - 'name' (str): The name of the fund.
        - 'creation_date' (date): The creation date of the fund.
        - 'investors' (list): A list of investors associated with the fund.
        - Other custom attributes, which may be None.
    """

    return get_settings().DefaultFunds


@lru_cache
def get_default_strategies() -> list[dict[str, str | date | list | None]]:
    """
    Retrieve the default strategies from the application settings.

    Returns:
        list[dict[str, Union[str, date, List, None]]]: A list of dictionaries
            representing default strategies. Each dictionary contains keys representing
            strategy attributes. Possible attributes include:
            - 'name' (str): The name of the strategy.
            - 'start_date' (date): The start date of the strategy.
            - 'indicators' (list): A list of indicators used in the strategy.
            - Other custom attributes, which may be None.
    """

    return get_settings().DefaultStrategies


@lru_cache
def get_backtesting_settings() -> Backtesting:
    """
    Retrieve the backtesting settings from the application settings.

    Returns:
        Backtesting: An instance of the Backtesting class containing backtesting
            configuration.
    """

    return get_settings().Backtesting


@lru_cache
def get_default_tickers() -> list[str]:
    """
    Retrieve the default tickers for backtesting.

    Returns:
        list[str]: A list of strings representing default tickers used in backtesting.
    """

    return get_backtesting_settings().Tickers


@lru_cache
def get_trading_tickers() -> list[str]:
    """
    Retrieve the tickers available for live trading.

    Returns:
        list[str]: A list of strings representing tickers available for live trading.
    """

    return get_settings().TradingTickers


@lru_cache
def get_trading_risk_management_settings() -> TradingRiskManagement:
    """
    Retrieve the trading risk management settings for live trading.

    Returns:
        TradingRiskManagement: A class containing default information relatively to
    """

    return get_settings().TradingRiskManagement
