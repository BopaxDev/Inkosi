from enum import StrEnum


class EnhancedStrEnum(StrEnum):
    """
    A custom enumeration class with enhanced features.

    Methods:
        has(cls, key: str) -> bool: Check if a given key exists in the enumeration.
        list(cls) -> List[str]: Get a list of all values in the enumeration.
    """

    @classmethod
    def has(
        cls,
        key: str,
    ) -> bool:
        """
        Check if a given key exists in the enumeration.

        Parameters:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """

        return key in cls.__members__.values()

    @classmethod
    def list(cls) -> list[str]:
        """
        Get a list of all values in the enumeration.

        Returns:
            list[str]: A list of all values.
        """

        return list(cls.__members__.values())


class GeneralPolicies(EnhancedStrEnum):
    """
    Enumeration class for general policies.

    Values:
        ACCESS_LOGIN (str): Access login policy.
    """

    ACCESS_LOGIN: str = "ACCESS_LOGIN"


class AdministratorPolicies(EnhancedStrEnum):
    """
    Enumeration class for administrator policies.

    Values:
        ADMINISTRATOR_IFM_FULL_ACCESS (str): Full access for Investment Firm
        administrators.
        ADMINISTRATOR_FM_FULL_ACCESS (str): Full access for Fund administrators.
        ADMINISTRATOR_PM_FULL_ACCESS (str): Full access for Portfolio Manager
        administrators.
    """

    ADMINISTRATOR_IFM_FULL_ACCESS: str = "ADMINISTRATOR_IFM_FULL_ACCESS"
    ADMINISTRATOR_FM_FULL_ACCESS: str = "ADMINISTRATOR_FM_FULL_ACCESS"
    ADMINISTRATOR_PM_FULL_ACCESS: str = "ADMINISTRATOR_PM_FULL_ACCESS"


class InvestorPolicies(EnhancedStrEnum):
    """
    Enumeration class for investor policies.

    Values:
        INVESTOR_DASHBOARD_VISUALISATION (str): Visualization access for investors.
        INVESTOR_SAMPLING_SCENARIOS (str): Scenarios sampling access for investors.
        INVESTOR_BACKTEST_ALL (str): Backtesting access for investors.
    """

    INVESTOR_DASHBOARD_VISUALISATION: str = "INVESTOR_DASHBOARD_VISUALISATION"
    INVESTOR_SAMPLING_SCENARIOS: str = "INVESTOR_SAMPLING_SCENARIOS"
    INVESTOR_BACKTEST_ALL: str = "INVESTOR_BACKTEST_ALL"


class CommissionTypes(EnhancedStrEnum):
    """
    Enumeration class for commission types.

    Values:
        PERCENTUAL_TYPE (str): Percentual commission type.
        ABSOLUTE_TYPE (str): Absolute commission type.
    """

    PERCENTUAL_TYPE: str = "percentual"
    ABSOLUTE_TYPE: str = "absolute"
