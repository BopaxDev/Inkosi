from dataclasses import dataclass, field

from inkosi.utils.utils import EnhancedStrEnum


class Templates(EnhancedStrEnum):
    NEW_ADMINISTRATOR: str = "new_administrator"
    NEW_FUND: str = "new_fund"


@dataclass
class NewFund:
    fund_name: str


@dataclass
class EmailReceivedAdministratorFundRaising:
    administrator_received: list[str]
    administrator_not_received: dict[str, str] = field(default_factory={})
