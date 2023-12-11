from inkosi.utils.utils import EnhancedStrEnum


class LogType(EnhancedStrEnum):
    """
    Enumeration class representing different log types.

    Attributes:
        CRITICAL (str): Critical log type.
        DEBUG (str): Debug log type.
        ERROR (str): Error log type.
        INFO (str): Information log type.
        WARN (str): Warning log type.
    """

    CRITICAL: str = "CRITICAL"
    DEBUG: str = "DEBUG"
    ERROR: str = "ERROR"
    INFO: str = "INFORMATION"
    WARN: str = "WARNING"
