from collections import namedtuple
from dataclasses import dataclass
from app.validators.tec_contribution_validator import TECRecordValidator
from app.models.tec_contribution_model import TECRecord
from typing import Callable, Generator, List


@dataclass
class CampaignFinanceConfig:
    STATE: str = 'Texas'
    VALIDATOR: Callable[[dict, ...], TECRecordValidator] = TECRecordValidator
    SQL_MODEL: Callable[[dict, ...], TECRecord] = TECRecord
    STATE_CAMPAIGN_FINANCE_AGENCY: str = 'TEC'
    EXPENSE_FILE_PREFIX: str = 'expend'
    CONTRIBUTION_FILE_PREFIX: str = 'contribs'
    ZIPFILE_URL: str = "https://www.ethics.state.tx.us/data/search/cf/TEC_CF_CSV.zip",

    VENDOR_NAME_COLUMN: str = 'payeeCompanyName'
    FILER_NAME_COLUMN: str = 'filerNameFormatted'

    PAYMENT_RECEIVED_DATE_COLUMN: str = 'receivedDt'
    EXPENDITURE_DATE_COLUMN: str = 'expendDt'
    CONTRIBUTION_DATE_COLUMN: str = 'contributionDt'

    EXPENDITURE_AMOUNT_COLUMN: str = 'expendAmount'

    RECORD_TYPE_COLUMN: str = 'recordType'

    RECORD_CATEGORY_TUPLE: Callable[[str, Generator], namedtuple] = namedtuple('category', ['name', 'records'])

    DATE_COLUMNS = [PAYMENT_RECEIVED_DATE_COLUMN, EXPENDITURE_DATE_COLUMN, CONTRIBUTION_DATE_COLUMN]
    UPPERCASE_COLUMNS = [VENDOR_NAME_COLUMN, FILER_NAME_COLUMN]
