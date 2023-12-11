from dataclasses import dataclass
from typing import TypeAlias

from inkosi.utils.utils import EnhancedStrEnum

ComparisonElement: TypeAlias = dict[str, int | float | str]

Colors: list[str] = [
    "#4c78a8",
    "#f58518",
    "#e45756",
    "#72b7b2",
    "#54a24b",
    "#eeca3b",
    "#b279a2",
    "#ff9da6",
    "#9d755d",
    "#bab0ac",
]


class Elements(EnhancedStrEnum):
    """
    Enumeration class representing various elements used in a financial context.

    Attributes:
        ELEMENT (str): Identifier for a generic element.
        PERIOD (str): Identifier for a period element.
        CLOSE_PRICE (str): Identifier for a close price element.
    """

    ELEMENT: str = "ELEMENT"
    PERIOD: str = "PERIOD"

    CLOSE_PRICE: str = "Close"


class AvailableRawColumns(EnhancedStrEnum):
    """
    Enumeration class representing available raw columns in a financial context.

    Attributes:
        DATES (str): Identifier for dates.
        OPEN_PRICE (str): Identifier for open price.
        HIGH_PRICE (str): Identifier for high price.
        LOW_PRICE (str): Identifier for low price.
        CLOSE_PRICE (str): Identifier for close price.
        RETURNS (str): Identifier for returns.
    """

    DATES: str = "Dates"
    OPEN_PRICE: str = "Open"
    HIGH_PRICE: str = "High"
    LOW_PRICE: str = "Low"
    CLOSE_PRICE: str = "Close"
    RETURNS: str = "Returns"


class VisualisationOptions(EnhancedStrEnum):
    """
    Enumeration class representing visualization options in a financial context.

    Attributes:
        OPEN_PRICE (str): Identifier for open price.
        HIGH_PRICE (str): Identifier for high price.
        LOW_PRICE (str): Identifier for low price.
        CLOSE_PRICE (str): Identifier for close price.
        RETURNS (str): Identifier for returns.
    """

    OPEN_PRICE: str = "Open"
    HIGH_PRICE: str = "High"
    LOW_PRICE: str = "Low"
    CLOSE_PRICE: str = "Close"
    RETURNS: str = "Returns"


class Relation(EnhancedStrEnum):
    """
    Enumeration class representing relational operators in a financial context.

    Attributes:
        GREATER (str): Greater than operator.
        GREATER_THAN (str): Greater than or equal to operator.
        LESS (str): Less than operator.
        LESS_THAN (str): Less than or equal to operator.
        EQUAL (str): Equal to operator.
    """

    GREATER: str = ">"
    GREATER_THAN: str = ">="
    LESS: str = "<"
    LESS_THAN: str = "<="
    EQUAL: str = "=="


class AvailableTechincalIndicators(EnhancedStrEnum):
    """
    Enumeration class representing available technical indicators in a financial
    context.

    Attributes:
        SMA (str): Simple Moving Average.
        WMA (str): Weighted Moving Average.
        EMA (str): Exponential Moving Average.
    """

    SMA: str = "SMA"
    WMA: str = "WMA"
    EMA: str = "EMA"


class TimeFrames(EnhancedStrEnum):
    """
    Enumeration class representing various time frames in a financial context.

    Attributes:
        MINUTES_1 (str): 1-minute time frame.
        MINUTES_2 (str): 2-minute time frame.
        MINUTES_5 (str): 5-minute time frame.
        MINUTES_15 (str): 15-minute time frame.
        MINUTES_30 (str): 30-minute time frame.
        MINUTES_60 (str): 60-minute time frame.
        MINUTES_90 (str): 90-minute time frame.
        HOUR_1 (str): 1-hour time frame.
        DAY_1 (str): 1-day time frame.
        DAY_5 (str): 5-day time frame.
        WEEK_1 (str): 1-week time frame.
        MONTH_1 (str): 1-month time frame.
        MONTH_3 (str): 3-month time frame.
    """

    MINUTES_1: str = "1m"
    MINUTES_2: str = "2m"
    MINUTES_5: str = "5m"
    MINUTES_15: str = "15m"
    MINUTES_30: str = "30m"
    MINUTES_60: str = "60m"
    MINUTES_90: str = "90m"
    HOUR_1: str = "1h"
    DAY_1: str = "1d"
    DAY_5: str = "5d"
    WEEK_1: str = "1wk"
    MONTH_1: str = "1mo"
    MONTH_3: str = "3mo"


class DataSourceType(EnhancedStrEnum):
    """
    Enumeration class representing data source types in a financial context.

    Attributes:
        YAHOO_FINANCE (str): Yahoo Finance as a data source.
    """

    YAHOO_FINANCE: str = "Yahoo Finance"


class SamplingMethods(EnhancedStrEnum):
    """
    Enumeration class representing various sampling methods.

    Attributes:
        NORMAL_DISTRIBUTION (str): Normal distribution sampling.
        LAPLACE_DISTRIBUTION (str): Laplace distribution sampling.
        UNIFORM_DISTRIBUTION (str): Uniform distribution sampling.
    """

    NORMAL_DISTRIBUTION: str = "Normal Sampling"
    LAPLACE_DISTRIBUTION: str = "Laplace Sampling"
    UNIFORM_DISTRIBUTION: str = "Uniform Sampling"


@dataclass
class Filter:
    """
    Data class representing a filter for comparing two elements.

    Attributes:
        first_element (ComparisonElement): The first element for comparison.
        second_element (ComparisonElement): The second element for comparison.
        relation (Relation | None, optional): The relational operator for the
            comparison.
    """

    first_element: ComparisonElement
    second_element: ComparisonElement
    relation: Relation | None
