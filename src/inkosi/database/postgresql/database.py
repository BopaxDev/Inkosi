from hashlib import sha256

from beartype import beartype
from beartype.typing import Any, Iterable
from sqlalchemy import Engine, MetaData, TextClause, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema
from sqlalchemy_utils import create_database, database_exists

from inkosi.log.log import Logger
from inkosi.utils.exceptions import PostgreSQLConnectionError
from inkosi.utils.settings import (
    get_administrators_policies,
    get_investors_policies,
    get_postgresql_schema,
    get_postgresql_url,
)

from .schemas import AdministratorProfile, Fund, PoliciesUpdate, User, UserRole

logger = Logger(
    module_name="PostgreSQLDatabase", package_name="postgresql", database=False
)


class DatabaseInstanceSingleton(
    type,
):
    _instance = None

    def __call__(
        cls,
        *args,
        **kwargs,
    ):
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
    def __init__(
        self,
    ) -> None:
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
        try:
            self.base.metadata.create_all(bind=self.engine)
        except Exception:
            logger.error(message="Unable to establish with the PostgreSQL Instance")
            raise PostgreSQLConnectionError

    @beartype
    def add(
        self,
        model: Iterable[declarative_base()] | declarative_base(),
    ) -> None:
        __session = sessionmaker(bind=self.engine)
        with __session() as session:
            if isinstance(model, Iterable):
                session.add_all(model)
            else:
                session.add(model)

            session.commit()
            session.close()

    @beartype
    def select(
        self,
        query: TextClause | str,
    ) -> list[Any]:
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
    ) -> None:
        __session = sessionmaker(bind=self.engine)
        with __session() as session:
            session.execute(query if isinstance(query, TextClause) else text(query))
            session.commit()
            session.close()


class PostgreSQLCrud:
    def __init__(self) -> None:
        self.postgresql_instance = PostgreSQLInstance()

    def get_users(
        self,
        email_address: str,
        password: str,
    ) -> list[User]:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT id,"
            " CONCAT(first_name, ' ', second_name) AS full_name, first_name,"
            f" second_name, email_address, '{UserRole.ADMINISTRATOR}' AS role FROM"
            f" administrators WHERE email_address = '{email_address}' AND password ="
            f" '{sha256(password.encode()).hexdigest()}' UNION ALL SELECT id,"
            " CONCAT(first_name, ' ', second_name) AS full_name, first_name,"
            f" second_name, email_address, '{UserRole.INVESTOR}' AS role FROM investors"
            f" WHERE email_address = '{email_address}' AND password ="
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
            f"SET search_path TO {get_postgresql_schema()}; SELECT CONCAT(first_name, '"
            " ', second_name) AS full_name, first_name, second_name, email_address,"
            f" policies, '{UserRole.ADMINISTRATOR}' AS role FROM administrators WHERE"
            f" email_address = '{email_address}';"
        )

        return [
            AdministratorProfile(**row._asdict())
            for row in self.postgresql_instance.select(query=__query)
        ]

    def get_portfolio_managers(
        self,
    ) -> list[AdministratorProfile]:
        __query = (
            f"SET search_path TO {get_postgresql_schema()}; SELECT CONCAT(first_name, '"
            " ', second_name) AS full_name, first_name, second_name, email_address,"
            f" policies, '{UserRole.ADMINISTRATOR}' AS role FROM administrators WHERE"
            " 'portfolio_manager_full_access' = ANY(policies);"
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
            " portfolio_managers, investors FROM funds"
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
