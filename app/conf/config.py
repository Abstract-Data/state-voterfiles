from dataclasses import dataclass
from app.validators.tec_expenditure_validator import TECExpenseValidator
from app.validators.tec_contribution_validator import TECContributionValidator
from app.models.tec_contribution_model import TECContributionRecord
from app.models.tec_expense_model import TECExpenseRecord
from typing import Callable, Generator
from app.loaders.toml_loader import TomlLoader
from app.conf.logger import CampaignFinanceLogger
import pandas as pd


logger = CampaignFinanceLogger(__file__)


@dataclass
class FileCategory:
    kind: str
    files: Generator


@dataclass
class CampaignFinanceConfig:
    STATE = TomlLoader('Texas').config
    STATE_AGENCY = STATE['STATE-FIELD-MAPPING']['state']['agency']['name']
    ZIPFILE_URL = STATE['STATE-FIELD-MAPPING']['state']['agency']['download-url']

    EXPENSE_VALIDATOR: Callable[[dict, ...], TECExpenseValidator] = TECExpenseValidator
    CONTRIBUTION_VALIDATOR: Callable[[dict, ...], TECContributionValidator] = TECContributionValidator

    EXPENSE_SQL_MODEL: Callable[[dict, ...], TECExpenseRecord] = TECExpenseRecord
    CONTRIBUTION_SQL_MODEL: Callable[[dict, ...], TECContributionRecord] = TECContributionRecord
    RECORD_CATEGORY = FileCategory

    EXPENSE_FILE_PREFIX = STATE['STATE-FIELD-MAPPING']['file-prefixes']['expenditures']
    CONTRIBUTION_FILE_PREFIX = STATE['STATE-FIELD-MAPPING']['file-prefixes']['contributions']

    VENDOR_NAME_COLUMN: str = STATE['FILE-VENDOR-PAYMENT-DETAILS']['name']
    CONTRIBUTOR_NAME_COLUMN: str = STATE['FILE-CONTRIBUTOR-DETAILS']['name']
    FILER_NAME_COLUMN: str = STATE['FILE-FILER-DETAILS']['person']['formatted']

    PAYMENT_RECEIVED_DATE_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['date-time']['payment-received']
    EXPENDITURE_DATE_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['date-time']['expenditures']
    CONTRIBUTION_DATE_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['date-time']['contributions']

    EXPENDITURE_AMOUNT_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['amounts']['expenditures']
    CONTRIBUTION_AMOUNT_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['amounts']['contributions']

    RECORD_TYPE_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['record-type']
    TYPE_EXPENSE: str = STATE['STATE-FIELD-MAPPING']['expenditures']['type_classifier']
    TYPE_CONTRIBUTION: str = STATE['STATE-FIELD-MAPPING']['contributions']['type_classifier']

    DATE_COLUMNS = [PAYMENT_RECEIVED_DATE_COLUMN, EXPENDITURE_DATE_COLUMN, CONTRIBUTION_DATE_COLUMN]
    UPPERCASE_COLUMNS = [VENDOR_NAME_COLUMN, FILER_NAME_COLUMN]


    @staticmethod
    def create_file_category(kind: str, records: Generator) -> FileCategory:
        return FileCategory(kind, records)


if __name__ != '__main__':
    logger.info('Config loaded')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 1000)
    settings = CampaignFinanceConfig()
