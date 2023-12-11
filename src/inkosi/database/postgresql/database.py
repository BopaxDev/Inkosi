from datetime import datetime, timedelta
from hashlib import sha256

from beartype import beartype
from beartype.typing import Any, Iterable
from psycopg2.errors import UniqueViolation
from sqlalchemy import Engine, MetaData, TextClause, create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema
from sqlalchemy_utils import create_database, database_exists

from inkosi.app.schemas import Mode
from inkosi.database.postgresql.schemas import (
    AdministratorProfile,
    ATSProfile,
    AuthenticationOutput,
    Commission,
    Fund,
    FundInformation,
    InvestorProfile,
    PoliciesUpdate,
    Tables,
    User,
    UserRole,
)
from inkosi.log.log import Logger
from inkosi.utils.exceptions import PostgreSQLConnectionError
from inkosi.utils.settings import (
    get_administrators_policies,
    get_investors_policies,
    get_ip_address_correspondence,
    get_postgresql_schema,
    get_postgresql_url,
    get_time_activity,
)
from inkosi.utils.utils import AdministratorPolicies

logger = Logger(
    module_name="PostgreSQLDatabase",
    package_name="postgresql",
    database=False,
)


class DatabaseInstanceSingleton(type):
    """
    Metaclass implementing the Singleton pattern for a database instance.

    Attributes:
        _instance: The singleton instance of the class.

    Methods:
        __call__(cls, *args, **kwargs):
            Override the call method to implement the Singleton pattern.

    Note:
        This metaclass ensures that only one instance of the class is created,
        following the Singleton pattern.
    """

    _instance = None

    def __call__(
        cls,
        *args,
        **kwargs,
    ):
        """
        Override the call method to implement the Singleton pattern.

        Parameters:
            cls: The class.
            *args: Variable arguments.
            **kwargs: Keyword arguments.

        Returns:
            The singleton instance of the class.
        """

        if not cls._instance:
            cls._instance = super(
                type(
                    cls,
                ),
                cls,
            ).__call__(
                *args,
                **kwargs,
            )

        return cls._instance


class PostgreSQLInstance(metaclass=DatabaseInstanceSingleton):
    """
    Singleton class representing a PostgreSQL database instance.

    Attributes:
        engine (Engine): The SQLAlchemy database engine.
        metadata (MetaData): The SQLAlchemy metadata object.
        base (declarative_base): The SQLAlchemy declarative base.

    Methods:
        __init__(self): Initialize the PostgreSQL instance.
        connect(self): Connect to the PostgreSQL instance.
        add(self, model: Iterable[declarative_base()] | declarative_base()) -> bool:
            Add records to the database.
        select(self, query: TextClause | str) -> list[Any]:
            Execute a select query on the database.
        update(self, query: TextClause | str) -> bool:
            Execute an update query on the database.

    Note:
        This class represents a singleton PostgreSQL database instance. It provides
        methods for connecting to the database, adding records, executing select
        queries, and executing update queries.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the PostgreSQL instance.

        Raises:
            PostgreSQLConnectionError: If unable to establish a connection with the
            PostgreSQL instance.
        """

        self.engine: Engine = create_engine(
            get_postgresql_url(),
        )

        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        __session = sessionmaker(bind=self.engine)
        with __session() as session:
            session.execute(
                CreateSchema(
                    name=get_postgresql_schema(),
                    if_not_exists=True,
                )
            )
            session.commit()

        self.metadata = MetaData(schema=get_postgresql_schema())

        self.base = declarative_base(metadata=self.metadata)

    def connect(
        self,
    ) -> None:
        """
        Connect to the PostgreSQL instance.

        Raises:
            PostgreSQLConnectionError: If unable to establish a connection with the
            PostgreSQL instance.
        """

        try:
            self.base.metadata.create_all(bind=self.engine)
        except Exception:
            logger.error(message="Unable to establish with the PostgreSQL Instance")
            raise PostgreSQLConnectionError

    @beartype
    def add(
        self,
        model: Iterable[declarative_base()] | declarative_base(),
    ) -> bool:
        """
        Add records to the database.

        Parameters:
            model (Iterable[declarative_base()] | declarative_base()): The model or
            iterable of models to add.

        Returns:
            bool: True if the addition is successful, False otherwise.
        """

        __session = sessionmaker(bind=self.engine)
        with __session() as session:
            try:
                if isinstance(model, Iterable):
                    session.add_all(model)
                else:
                    session.add(model)

                session.commit()
            except IntegrityError as error:
                if isinstance(error.orig, UniqueViolation):
                    logger.warn("Another record has been found")
                    return False
                logger.error(
                    "Unable to add the specified records to the database. Error"
                    f" occurred: {error}"
                )
                return False
            except Exception as error:
                logger.error(
                    "Unable to add the specified records to the database. Error"
                    f" occurred: {error}"
                )

                return False
            else:
                session.close()
                return True

    @beartype
    def select(
        self,
        query: TextClause | str,
    ) -> list[Any]:
        """
        Execute a select query on the database.

        Parameters:
            query (TextClause | str): The select query.

        Returns:
            list[Any]: The result of the select query.
        """

        __session = sessionmaker(bind=self.engine)
        with __session() as session:
            __query = session.execute(
                query if isinstance(query, TextClause) else text(query)
            )
            result = __query.all()
            session.close()

            return result

    @beartype
    def update(
        self,
        query: TextClause | str,
    ) -> bool:
        """
        Execute an update query on the database.

        Parameters:
            query (TextClause | str): The update query.

        Returns:
            bool: True if the update is successful, False otherwise.
        """

        __session = sessionmaker(bind=self.engine)
        with __session() as session:
            try:
                session.execute(query if isinstance(query, TextClause) else text(query))
                session.commit()
                session.close()
            except Exception as error:
                logger.error(
                    f"Unable to update records on the database. Error occurred: {error}"
                )
                return False
            else:
                return True


class PostgreSQLCrud:
    def __init__(self) -> None:
        self.postgresql_instance = PostgreSQLInstance()

    def valid_authentication(
        self,
        token_id: str,
        ip_address: str | None = None,
    ) -> bool:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT id, created_at,"
            " validity, user_id, ip_address FROM authentication WHERE id ="
            f" '{token_id}' AND mode = '{Mode.WEBAPP}';"
        )

        if get_ip_address_correspondence():
            __query += (
                " AND ip_address ="
                f" '{ip_address if isinstance(ip_address, str) else ''}';"
            )

        result = [
            AuthenticationOutput(**row._asdict())
            for row in self.postgresql_instance.select(query=__query)
        ]

        match len(result):
            case 1:
                row = result[0]
                created_at = row.created_at
                if datetime.now() <= created_at + timedelta(**get_time_activity()):
                    self.postgresql_instance.update(
                        f"SET search_path TO {get_postgresql_schema()}; DELETE FROM"
                        f" {Tables.AUTHENTICATION} WHERE id <> '{token_id}' AND user_id"
                        f" = '{row.user_id}';"
                    )
                    return True
                else:
                    self.postgresql_instance.update(
                        f"SET search_path TO {get_postgresql_schema()}; DELETE FROM"
                        f" {Tables.AUTHENTICATION} WHERE id = '{token_id}';"
                    )

        return False

    def valid_backtesting_token(
        self,
        token_id: str,
        ip_address: str | None = None,
    ) -> bool:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT id, created_at,"
            " validity, user_id, ip_address FROM authentication WHERE id ="
            f" '{token_id}';"
        )

        if get_ip_address_correspondence():
            __query += (
                " AND ip_address ="
                f" '{ip_address if isinstance(ip_address, str) else ''}';"
            )

        result = [
            AuthenticationOutput(**row._asdict())
            for row in self.postgresql_instance.select(query=__query)
        ]

        match len(result):
            case 1:
                row = result[0]
                created_at = row.created_at
                if datetime.now() <= created_at + timedelta(**get_time_activity()):
                    self.postgresql_instance.update(
                        f"SET search_path TO {get_postgresql_schema()}; DELETE FROM"
                        f" {Tables.AUTHENTICATION} WHERE id <> '{token_id}' AND user_id"
                        f" = '{row.user_id}';"
                    )
                    return True
                else:
                    self.postgresql_instance.update(
                        f"SET search_path TO {get_postgresql_schema()}; DELETE FROM"
                        f" {Tables.AUTHENTICATION} WHERE id = '{token_id}';"
                    )

        return False

    def get_users(
        self,
        email_address: str,
        password: str,
    ) -> list[User]:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT id,"
            " CONCAT(first_name, ' ', second_name) AS full_name, first_name,"
            f" second_name, email_address, '{UserRole.ADMINISTRATOR}' AS role, policies"
            f" FROM administrators WHERE CAST(id AS TEXT) = '{email_address}' AND"
            f" password = '{sha256(password.encode()).hexdigest()}' UNION ALL SELECT"
            " id, CONCAT(first_name, ' ', second_name) AS full_name, first_name,"
            f" second_name, email_address, '{UserRole.INVESTOR}' AS role, policies FROM"
            f" investors WHERE email_address = '{email_address}' AND password ="
            f" '{sha256(password.encode()).hexdigest()}';"
        )

        return [
            User(**row._asdict())
            for row in self.postgresql_instance.select(query=__query)
        ]

    def get_administrator_by_email_address(
        self,
        email_address: str,
    ) -> list[AdministratorProfile]:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT id,"
            " CONCAT(first_name, ' ', second_name) AS full_name, first_name,"
            f" second_name, email_address, policies, '{UserRole.ADMINISTRATOR}' AS role"
            f" FROM administrators WHERE email_address = '{email_address}';"
        )

        return [
            AdministratorProfile(**row._asdict())
            for row in self.postgresql_instance.select(query=__query)
        ]

    def get_investor_by_email_address(
        self,
        email_address: str,
    ) -> list[AdministratorProfile]:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT id,"
            " CONCAT(first_name, ' ', second_name) AS full_name, first_name,"
            f" second_name, email_address, policies, '{UserRole.ADMINISTRATOR}' AS role"
            f" FROM investors WHERE email_address = '{email_address}';"
        )

        return [
            InvestorProfile(**row._asdict())
            for row in self.postgresql_instance.select(query=__query)
        ]

    def get_ats_by_id(
        self,
        ats_id: str,
    ) -> list[ATSProfile]:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT strategies.id,"
            " CONCAT(administrators.first_name, ' ', administrators.second_name) AS"
            " full_name, administrators.id AS administrator_id, fund_names, category"
            " FROM strategies JOIN administrators ON administrators.id ="
            f" strategies.administrator_id WHERE strategies.id = '{ats_id}';"
        )

        return [
            ATSProfile(**row._asdict())
            for row in self.postgresql_instance.select(query=__query)
        ]

    def get_portfolio_managers(
        self,
    ) -> list[AdministratorProfile]:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT id,"
            " CONCAT(first_name, ' ', second_name) AS full_name, first_name,"
            f" second_name, email_address, policies, '{UserRole.ADMINISTRATOR}' AS role"
            " FROM administrators WHERE"
            f" '{AdministratorPolicies.ADMINISTRATOR_PM_FULL_ACCESS}' = ANY(policies);"
        )

        return [
            AdministratorProfile(**row._asdict())
            for row in self.postgresql_instance.select(query=__query)
        ]

    def get_funds(
        self,
    ) -> list[Fund]:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT id, fund_name,"
            " investment_firm, created_at, administrators, investors,"
            " capital_distribution, commission_type, commission_value, risk_limits,"
            " raising_funds FROM funds"
        )

        return [
            Fund(**row._asdict())
            for row in self.postgresql_instance.select(query=__query)
        ]

    def update_policies(
        self,
        policies_update: PoliciesUpdate,
    ) -> bool:
        if not UserRole.has(policies_update.role):
            logger.critical(
                message=(
                    "Unable to update the policies of an unknown type of user (User ID:"
                    f" {policies_update.user_id})."
                )
            )
            return False

        if isinstance(policies_update.policies, str):
            policies_update.policies = [policies_update.policies]

        match policies_update.role:
            case UserRole.ADMINISTRATOR:
                policies_update.policies: list[str] = list(
                    set(policies_update.policies).intersection(
                        set(get_administrators_policies())
                    )
                )
            case UserRole.INVESTOR:
                policies_update.policies: list[str] = list(
                    set(policies_update.policies).intersection(
                        set(get_investors_policies())
                    )
                )
            case _:
                logger.critical(message="Unable to identify the role")
                return False

        __query = (
            f"SET search_path TO {get_postgresql_schema()}; UPDATE administrators SET"
            " policies = (SELECT array_agg(distinct e) FROM unnest(policies ||"
            f" array[{', '.join([x.__repr__() for x in policies_update.policies])}]"
            f"::text[]) e) WHERE id = {policies_update.user_id};"
        )

        self.postgresql_instance.update(query=__query)
        return True

    def get_fund_information(
        self,
        fund_name: str | None,
    ) -> list[FundInformation]:
        where_clause = f"WHERE fund_name = '{fund_name}';"

        if fund_name is None:
            where_clause = ";"

        __query = (
            f"SET search_path TO {get_postgresql_schema()}; WITH tools(id) AS (SELECT"
            f" id FROM strategies WHERE '{fund_name}' = ANY(fund_names)),"
            " administrators_of_fund(id) AS (SELECT unnest(administrators) as id from"
            f" funds WHERE fund_name='{fund_name}'), investors_of_fund(id) AS (SELECT"
            f" unnest(investors) as id from funds WHERE fund_name='{fund_name}') SELECT"
            " DISTINCT funds.id, fund_name, created_at, investment_firm,"
            " administrators, array(SELECT CONCAT(first_name, ' ', second_name) AS"
            " title FROM development.administrators JOIN administrators_of_fund ON"
            " administrators_of_fund.id = administrators.id) AS"
            " administrators_full_name, investors, array(SELECT CONCAT(first_name, '"
            " ', second_name) AS title FROM development.investors JOIN"
            " investors_of_fund ON investors_of_fund.id = investors.id)"
            " AS investors_full_name, capital_distribution, commission_type,"
            " commission_value, array(SELECT DISTINCT id FROM development.strategies"
            f" WHERE '{fund_name}' = ANY(fund_names)) AS strategies, raising_funds FROM"
            f" funds, administrators_of_fund {where_clause}"
        )

        return [
            FundInformation(**row._asdict())
            for row in self.postgresql_instance.select(query=__query)
        ]

    def check_for_investor_existence(
        self,
        investor_id: int,
    ) -> bool:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT id FROM"
            f" investors WHERE id = '{str(investor_id)}';"
        )

        result = self.postgresql_instance.select(query=__query)
        match len(result):
            case 0:
                return False
            case 1:
                return True
            case _:
                logger.critical(
                    "Two or more investors have been found with the same id."
                )
                return False

    def check_for_administrator_existence(
        self,
        administrator_id: int,
    ) -> bool:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT id FROM"
            f" administrators WHERE id = '{str(administrator_id)}';"
        )

        result = self.postgresql_instance.select(query=__query)
        match len(result):
            case 0:
                return False
            case 1:
                return True
            case _:
                logger.critical(
                    "Two or more administrators have been found with the same id."
                )
                return False

    def check_for_fundname_existence(
        self,
        fund_name: str,
    ) -> bool:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT fund_name FROM"
            f" funds WHERE fund_name = '{fund_name}';"
        )

        result = self.postgresql_instance.select(query=__query)
        match len(result):
            case 0:
                return False
            case 1:
                return True
            case _:
                logger.critical("Two or more funds have been found with the same name.")
                return False

    def add_administrator_to_fund(
        self,
        administrator_id: int | None,
        fund: str | int,
    ) -> bool:
        if administrator_id is None:
            return False

        if isinstance(fund, int):
            where_option = f"WHERE id = {fund}"
        elif isinstance(fund, str):
            where_option = f"WHERE fund_name = '{fund}'"
        else:
            return False

        if self.check_for_administrator_existence(administrator_id=administrator_id):
            __query = (
                f"SET search_path TO {get_postgresql_schema()}; UPDATE funds SET"
                " administrators = (SELECT array(select distinct"
                f" unnest(array_append(administrators, {administrator_id})) FROM"
                f" funds)) {where_option};"
            )

            self.postgresql_instance.update(query=__query)
            return True
        else:
            return False

    def update_commission(
        self,
        commission: Commission,
    ) -> bool:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; UPDATE funds SET"
            f" commission_type = '{commission.commission_type}', commission_value ="
            f" {commission.commission_value} WHERE fund_name = '{commission.fund}'"
            f" OR id = {commission.fund};"
        )

        return self.postgresql_instance.update(query=__query)

    def get_fund_managers(
        self,
        fund_name: str | None = None,
    ) -> list[User]:
        if not fund_name:
            __query = (
                f"SET search_path TO {get_postgresql_schema()}; SELECT id,"
                " CONCAT(first_name, ' ', second_name) AS full_name, first_name,"
                f" second_name, email_address, policies, '{UserRole.ADMINISTRATOR}' AS"
                " role FROM administrators WHERE"
                f" '{AdministratorPolicies.ADMINISTRATOR_FM_FULL_ACCESS}' ="
                " ANY(policies) OR"
                f" '{AdministratorPolicies.ADMINISTRATOR_IFM_FULL_ACCESS}' ="
                " ANY(policies);"
            )

            return [
                AdministratorProfile(**row._asdict())
                for row in self.postgresql_instance.select(query=__query)
            ]
        else:
            __query = (
                f"SET search_path TO {get_postgresql_schema()}; WITH"
                " all_administrators(id, full_name) AS (SELECT id, CONCAT(first_name,"
                " ' ', second_name) AS full_name FROM administrators), difference(id,"
                " full_name) AS (SELECT id, full_name FROM all_administrators WHERE"
                " all_administrators.id NOT IN (SELECT UNNEST(administrators) AS id"
                f" FROM funds WHERE fund_name = '{fund_name}')) SELECT full_name, id"
                " FROM difference;"
            )

            raw_result = {}

            result = self.postgresql_instance.select(query=__query)
            for row in result:
                raw_result[row[0]] = row[1]

            return raw_result

    def conclude_fund_raising(
        self,
        fund_name: str,
    ) -> FundInformation:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; UPDATE "
            f"funds SET raising_funds = False WHERE fund_name = '{fund_name}';"
        )

        return self.postgresql_instance.update(query=__query)

    def deposit_fund(
        self,
        fund_name: str,
        investor_id: int,
        amount: float,
    ) -> bool:
        __query = (
            "UPDATE development.funds SET capital_distribution ="
            " JSONB_SET(capital_distribution, '{"
            f"{investor_id}"
            "}', "
            f"'{amount}') WHERE"
            f" fund_name='{fund_name}';"
        )

        return self.postgresql_instance.update(query=__query)
