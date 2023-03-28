from collections import namedtuple
from dataclasses import dataclass, field
from app.validators.tec_contribution_validator import TECRecordValidator
from app.models.tec_contribution_model import TECRecord
from typing import Callable, Generator, List, Type, Dict, ClassVar
from app.loaders.toml_loader import TomlLoader
from app.conf.logger import CampaignFinanceLogger


logger = CampaignFinanceLogger(__file__)


@dataclass
class FileCategory:
    kind: str
    files: Generator


@dataclass
class CampaignFinanceConfig:
    STATE = TomlLoader('Texas').config
    ZIPFILE_URL = STATE['STATE-FIELD-MAPPING']['state']['agency']['download-url']

    VALIDATOR: Callable[[dict, ...], TECRecordValidator] = TECRecordValidator
    SQL_MODEL: Callable[[dict, ...], TECRecord] = TECRecord
    RECORD_CATEGORY = FileCategory

    EXPENSE_FILE_PREFIX = STATE['STATE-FIELD-MAPPING']['file-prefixes']['expenditures']
    CONTRIBUTION_FILE_PREFIX = STATE['STATE-FIELD-MAPPING']['file-prefixes']['contributions']

    VENDOR_NAME_COLUMN: str = STATE['FILE-VENDOR-PAYMENT-DETAILS']['name']
    FILER_NAME_COLUMN: str = STATE['FILE-FILER-DETAILS']['name']

    PAYMENT_RECEIVED_DATE_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['date-time']['payment-received']
    EXPENDITURE_DATE_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['date-time']['expenditures']
    CONTRIBUTION_DATE_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['date-time']['contributions']

    EXPENDITURE_AMOUNT_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['amounts']['expenditures']
    CONTRIBUTION_AMOUNT_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['amounts']['contributions']

    RECORD_TYPE_COLUMN: str = STATE['STATE-FIELD-MAPPING']['columns']['record-type']
    RECORD_EXPENSE_TYPE: str = STATE['STATE-FIELD-MAPPING']['expenditures']['type_classifier']
    RECORD_CONTRIBUTION_TYPE: str = STATE['STATE-FIELD-MAPPING']['contributions']['type_classifier']

    DATE_COLUMNS = [PAYMENT_RECEIVED_DATE_COLUMN, EXPENDITURE_DATE_COLUMN, CONTRIBUTION_DATE_COLUMN]
    UPPERCASE_COLUMNS = [VENDOR_NAME_COLUMN, FILER_NAME_COLUMN]

    @staticmethod
    def create_file_category(kind: str, records: Generator) -> FileCategory:
        return FileCategory(kind, records)
