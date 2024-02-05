from typing import Any

from inkosi.database.postgresql.schemas import RaiseNewFund

from .schemas import EmailReceivedAdministratorFundRaising, Templates


class MailerMetaclass(type):
    template_downloaded: bool = False

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return super().__call__(*args, **kwds)


class Mailer(metaclass=MailerMetaclass):
    def __init__(self) -> None:
        pass

    def __send__(
        self,
        template: Templates,
        **kwds,
    ) -> bool:
        ...

    def send_email_to_administrator_for_fund_raising(
        self,
        raise_new_fund: RaiseNewFund,
    ) -> EmailReceivedAdministratorFundRaising:
        ...
