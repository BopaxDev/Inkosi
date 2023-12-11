import logging
from dataclasses import asdict

from beartype import beartype

from inkosi.database.mongodb.models import Log
from inkosi.log.models import LogType
from inkosi.utils.settings import get_mongodb_collection


class Logger:
    def __init__(
        self,
        module_name: str,
        log_filename: str | None = "master.log",
        level: int = logging.DEBUG,
        formatter: str = "[%(asctime)s\t %(levelname)s\t %(name)s] %(message)s",
        **kwargs,
    ) -> None:
        """
        Initialize a custom logger instance.

        Parameters:
            module_name (str): The name of the module for which the logger is created.
            log_filename (str | None, optional): The filename for the log file. Defaults
                to "master.log".
            level (int, optional): The logging level. Defaults to logging.DEBUG.
            formatter (str, optional): The log message format. Defaults to
                "[%(asctime)s\t %(levelname)s\t %(name)s] %(message)s".
            **kwargs: Additional keyword arguments.

        Attributes:
            module_name (str): The name of the module for which the logger is created.
            package_name (str | None): The name of the package if provided; otherwise,
            None.
            name (str): The logger name, including the package name if available.
            formatter (str): The log message format.
            logger (logging.Logger): The main logger instance.
            file_handler (logging.FileHandler | None): The file handler for writing
            logs to a file if log_filename is provided.
            stream_handler (logging.StreamHandler): The stream handler for writing logs
            to the console.
            mongo_manager: The MongoDB manager instance if database information is
            provided; otherwise, None.

        Note:
            This method initializes a custom logger instance for logging messages. It
            supports logging to both a file (if log_filename is provided) and the
            console. Additionally, it can initialize a MongoDB manager instance if
            database information is provided in the keyword arguments.
        """

        self.module_name = module_name
        self.package_name = None

        if kwargs.get("package_name", ""):
            self.package_name = kwargs.get("package_name")
            self.name = f"{self.package_name}:{self.module_name}"

        self.name = self.module_name

        self.formatter = formatter

        self.logger = logging.getLogger(
            name=self.name,
        )
        self.logger.setLevel(
            level=level,
        )

        if log_filename:
            self.file_handler = logging.FileHandler(
                log_filename,
            )

            self.file_handler.setFormatter(
                fmt=logging.Formatter(
                    formatter,
                ),
            )

            self.file_handler.setLevel(
                level=level,
            )

            self.logger.addHandler(
                self.file_handler,
            )

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(
            fmt=logging.Formatter(
                formatter,
            ),
        )

        self.stream_handler.setLevel(
            level=level,
        )

        self.logger.addHandler(
            hdlr=self.stream_handler,
        )

        self.mongo_manager = None

        if not kwargs.get(
            "database",
            None,
        ):
            if isinstance(kwargs.get("database"), bool):
                return

            from inkosi.database.mongodb.database import MongoDBInstance

            self.mongo_manager = MongoDBInstance()

    def critical(
        self,
        message: str,
    ) -> None:
        """
        Log a critical-level message and register it to the MongoDB database if
        available.

        Parameters:
            message (str): The message to be logged.

        Returns:
            None
        """

        self.logger.critical(
            msg=message,
        )

        self.__register_to_log__(
            log_type=LogType.CRITICAL,
            message=message,
        )

    def debug(
        self,
        message: str,
    ) -> None:
        """
        Log a debug-level message and register it to the MongoDB database if available.

        Parameters:
            message (str): The message to be logged.

        Returns:
            None
        """

        self.logger.debug(
            msg=message,
        )

        self.__register_to_log__(
            log_type=LogType.DEBUG,
            message=message,
        )

    def error(
        self,
        message: str,
    ) -> None:
        """
        Log an error-level message and register it to the MongoDB database if available.

        Parameters:
            message (str): The message to be logged.

        Returns:
            None
        """

        self.logger.error(
            msg=message,
        )

        self.__register_to_log__(
            log_type=LogType.ERROR,
            message=message,
        )

    def info(
        self,
        message: str,
    ) -> None:
        """
        Log an info-level message and register it to the MongoDB database if available.

        Parameters:
            message (str): The message to be logged.

        Returns:
            None
        """

        self.logger.info(
            msg=message,
        )

        self.__register_to_log__(
            log_type=LogType.INFO,
            message=message,
        )

    def warn(
        self,
        message: str,
    ) -> None:
        """
        Log a warning-level message and register it to the MongoDB database if
        available.

        Parameters:
            message (str): The message to be logged.

        Returns:
            None
        """

        self.logger.warning(
            msg=message,
        )

        self.__register_to_log__(
            log_type=LogType.WARN,
            message=message,
        )

    @beartype
    def __register_to_log__(
        self,
        log_type: LogType,
        message: str,
    ) -> None:
        """
        Register a log entry to the MongoDB database if available.

        Parameters:
            log_type (LogType): The log type.
            message (str): The log message.

        Returns:
            None
        """

        if not self.mongo_manager:
            return

        self.mongo_manager.database[get_mongodb_collection().Log].insert_one(
            asdict(
                Log(
                    PackageName=self.package_name,
                    ModuleName=self.module_name,
                    Level=log_type,
                    Message=message,
                )
            )
        )
