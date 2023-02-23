from pathlib import Path
import csv
from dataclasses import dataclass, field
from typing import List, Dict, ClassVar, Type, Generator
from app.conf.config import CampaignFinanceConfig
from pydantic import ValidationError
from app.conf.tec_postgres import SessionLocal, sessionmaker
import os
import sys
from tqdm import tqdm
from zipfile import ZipFile
import requests
import pandas as pd
import logging
from collections import namedtuple
from datetime import datetime

logger = logging.getLogger(__name__)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

tec_folder = Path.home() / 'Downloads' / "TEC_CF_CSV"

EXPENSE_FILE_COLUMNS = set()
CONTRIBUTION_FILE_COLUMNS = set()

RecordValidation = namedtuple('RecordValidation', ['passed', 'failed'])


def uppercase(series: pd.Series) -> pd.Series:
    return series.str.strip().str.upper()


def pandas_datetime(series: pd.Series) -> pd.to_datetime:
    return pd.to_datetime(series)


def currency_format(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        df[column] = df[column].fillna(0)
        if df[column].dtype == 'float':
            df[column] = df[column].map(lambda x: f"${x:,.2f}")

    df = df.replace('$0.00', '')
    return df


@dataclass
class TECFolderLoader:
    """
    TECFolderReader
    ===============
    This class is used to pull Campaign finance files from the TEC website.
    It is used to download the files from the TEC website and
    validate the data in the files.
    """
    _EXPENSE_FILE_PREFIX: str = CampaignFinanceConfig.EXPENSE_FILE_PREFIX
    _CONTRIBUTION_FILE_PREFIX: str = CampaignFinanceConfig.CONTRIBUTION_FILE_PREFIX
    _ZIPFILE_URL: str = CampaignFinanceConfig.ZIPFILE_URL
    expense_files: Generator[Dict[str, Path], None, None] = field(default_factory=list)
    contribution_files: Generator[Dict[str, Path], None, None] = field(default_factory=list)

    @property
    def folder(self) -> Path:
        fldr = Path.cwd()
        tmp = fldr / 'tmp'
        return tmp

    @folder.setter
    def folder(self, value) -> None:
        self.folder = value

    def file_list(self, prefix) -> Generator[Dict[str, Path], None, None]:
        if not self.folder.exists():
            raise FileNotFoundError(f'Folder {self.folder} does not exist')

        for f in self.folder.glob(f'{prefix}*'):
            yield {'name': f.name, 'file': f}

    def download(self, read_from_temp: bool = True) -> Path or object:
        tmp = self.folder
        temp_filename = tmp / 'TEC_CF_CSV.zip'

        def download_file() -> None:
            # download files
            with requests.get(self._ZIPFILE_URL, stream=True) as resp:
                # check header to get content length, in bytes
                total_length = int(resp.headers.get("Content-Length"))

                # Chunk download of zip file and write to temp folder
                print(f'Downloading {CampaignFinanceConfig.STATE_CAMPAIGN_FINANCE_AGENCY} Files...')
                with open(temp_filename, 'wb') as f:
                    for chunk in tqdm(resp.iter_content(
                            chunk_size=1024),
                            total=round(total_length / 1024, 2),
                            unit='KB',
                            desc='Downloading'):
                        if chunk:
                            f.write(chunk)
                    print('Download Complete')
                return None

        def extract_zipfile() -> None:
            # extract zip file to temp folder
            with ZipFile(temp_filename, 'r') as myzip:
                print('Extracting Files...')
                for _ in tqdm(myzip.namelist()):
                    myzip.extractall(tmp)
                os.unlink(temp_filename)
                self.folder = tmp  # set folder to temp folder

        try:

            if read_from_temp is False:
                # check if tmp folder exists
                if tmp.is_dir():
                    ask_to_make_folder = input("Temp folder already exists. Overwrite? (y/n): ")
                    if ask_to_make_folder.lower() == 'y':
                        print('Overwriting Temp Folder...')
                        download_file()
                        extract_zipfile()
                    else:
                        as_to_change_folder = input("Use temp folder as source? (y/n): ")
                        if as_to_change_folder.lower() == 'y':
                            if tmp.glob('*.csv') == 0 and tmp.glob('*.zip') == 1:
                                print('No CSV files in temp folder. Found .zip file...')
                                print('Extracting .zip file...')
                                extract_zipfile()
                            else:
                                self.folder = tmp  # set folder to temp folder
                            return self
                        else:
                            print('Exiting...')
                            sys.exit()

            else:
                self.folder = tmp  # set folder to temp folder

        # remove tmp folder if user cancels download
        except KeyboardInterrupt:
            print('Download Cancelled')
            print('Removing Temp Folder...')
            for file in tmp.iterdir():
                file.unlink()
            tmp.rmdir()
            print('Temp Folder Removed')

            return self

    def __post_init__(self):
        self.expense_files = self.file_list(self._EXPENSE_FILE_PREFIX)
        self.contribution_files = self.file_list(self._CONTRIBUTION_FILE_PREFIX)


@dataclass
class TECRecord:
    record: Dict
    category: str = field(init=False, repr=False)
    validator: CampaignFinanceConfig.VALIDATOR = field(init=False, repr=False)
    sql_model: CampaignFinanceConfig.SQL_MODEL = field(init=False, repr=False)

    def validate_record(self) -> CampaignFinanceConfig.VALIDATOR:
        self.validator = CampaignFinanceConfig.VALIDATOR(**self.record)
        return self.validator

    def create_sql_model(self) -> CampaignFinanceConfig.SQL_MODEL:
        self.sql_model = CampaignFinanceConfig.SQL_MODEL(**self.validator.dict())
        return self.sql_model

    def __post_init__(self):
        self.category = self.record[CampaignFinanceConfig.RECORD_TYPE_COLUMN]


@dataclass
class TECFileReader:
    """
    TECFileReader
    =============
    This class is used to read TEC campaign finance files.
    It is used to read the files from the TEC website and
    validate the data in the files.
    """
    folder_obj: TECFolderLoader = TECFolderLoader()
    category: CampaignFinanceConfig.RECORD_CATEGORY_TUPLE = CampaignFinanceConfig.RECORD_CATEGORY_TUPLE
    FILE_VALIDATOR: ClassVar[Type[CampaignFinanceConfig.VALIDATOR]] = CampaignFinanceConfig.VALIDATOR

    @staticmethod
    def read(file) -> Generator[Dict[str, str], None, None]:
        opn = open(file['file'], 'r')
        for _record in tqdm(csv.DictReader(opn), desc=f'Reading {file["name"]}', unit=' records'):
            r = TECRecord(_record)
            yield r

    @staticmethod
    def read_files(file_list: Generator[Dict[str, Path], None, None]) -> Generator[TECRecord, None, None]:
        for file in file_list:
            reader = TECFileReader.read(file)
            for _record in reader:
                yield _record

    @staticmethod
    def load_records(list_name: Generator) -> Dict[int, Dict[str, str]]:
        def records():
            for file in list_name:
                for _record in file:
                    yield TECRecord(_record, file.category)
        _records = records()
        return {i: record for i, record in enumerate(_records)}

    def __post_init__(self):
        self.path: Path = field(default_factory=Path)

        self.contributions: TECFileReader.category = TECFileReader.category(
            'contribution',
            TECFileReader.read_files(self.folder_obj.contribution_files)
        )

        self.expenses: TECFileReader.category = TECFileReader.category(
            'expense',
            TECFileReader.read_files(self.folder_obj.expense_files)
        )


@dataclass
class CreatePydanticModel:

    category: TECFileReader.category = TECFileReader.category
    record_category: str = CampaignFinanceConfig.RECORD_CATEGORY_TUPLE
    _record_types: Dict[str, str] = field(default_factory=dict)

    def create_record_types(self) -> Dict[str, str]:
        self._record_types = {
            key: value for key, value in [
                var for _record in next(self.category.records) for var in _record
            ]
        }
        self._record_types[CampaignFinanceConfig.RECORD_TYPE_COLUMN] = self.record_category
        return self._record_types

    def create_validator(self, validator_name: str) -> None:
        """
        Create Validator
        :return:
        """
        print(f"class {validator_name}(BaseModel):")
        for key, value in self._record_types.items():
            print(f"\t{key}: Optional[{type(value).__name__}]")

        print(f"""\tclass Config:
            \torm_mode = True
            \tallow_population_by_field_name = True
            \tvalidate_assignment = True
            \tvalidate_all = True
            \textra = 'forbid'""")

    def create_sql_model(self, model_name: str, table_name: str, schema: str = CampaignFinanceConfig.STATE) -> None:
        if table_name or schema is None:
            raise ValueError(f"""
                Table name and schema are required to create a SQL model:
                table_name: {table_name}
                schema: {schema}""")

        print(f"""class {model_name}(Base):""")
        print(f"\t__tablename__ = '{table_name}'")
        print(f"\t__table_args__ = {{'schema': '{schema.lower()}'}}")
        for _name, _type in self._record_types.items():
            if _type == str:
                _type_details = "Column(String, nullable=True)"
            elif _type == int:
                _type_details = "Column(Integer, nullable=True)"
            elif _type == float:
                _type_details = "Column(Float, nullable=True)"
            elif _type == datetime:
                _type_details = "Column(DateTime, nullable=True)"
            else:
                _type_details = "Column(String, nullable=True)"
            print(f"\t{_name} = {_type_details}")


@dataclass
class TECRecordValidation:
    """
    TECRecordValidation
    ===================
    This class is used to validate the TEC campaign finance data.
    """
    file: TECFileReader.category
    passed: List[Dict] = field(init=False)
    failed: List[str] = field(init=False)
    _record_cateogry: str = field(init=False)
    _record_types: Dict[str, str] = field(init=False)

    @property
    def records(self):
        return self.file.records

    @property
    def record_category(self):
        return self.file.name

    def validate(self, load_to_sql: bool = False) -> [List[Dict], List[Dict]]:
        self.passed, self.failed = [], []
        _sql_queue, _sql_queue_count = [], 0
        for _record in self.records:
            try:
                _record.validate_record()
                self.passed.append(_record.validator.dict())
                if load_to_sql:
                    _record.create_sql_model()
                    _sql_queue.append(_record.sql_model)
                    if len(_sql_queue) == 50000:
                        self.sql_loader(_sql_queue)
                        _sql_queue_count += len(_sql_queue)
                        print("\r" + f"Loaded {_sql_queue_count:,} records to SQL")
                        _sql_queue = []

            except ValidationError as e:
                errors = e.json()
                self.failed.append({'errors': errors,
                                    'record': _record})
        if load_to_sql:
            self.sql_loader(_sql_queue)
            _sql_queue_count += len(_sql_queue)
            print("\r" + f"Loaded {_sql_queue_count:,} records to SQL")

        sys.stdout.write(
            f"""\r=== Validation Results for {CampaignFinanceConfig.STATE} {self.record_category.title()} Records ===
            \rPassed: {len(self.passed):,}
            \rFailed: {len(self.failed):,}
            """)

        if load_to_sql:
            print(f"\rLoaded {len(self.passed):,} records to SQL")
        sys.stdout.flush()

        return self.passed, self.failed

    @staticmethod
    def sql_loader(models: List, session: sessionmaker = SessionLocal):
        with session() as db:
            db.add_all(models)
            db.commit()

    @staticmethod
    def load_file_to_sql(models: Generator, session: sessionmaker = SessionLocal):
        error_records = []
        records_to_load = []
        with session() as db:
            for record in models:
                records_to_load.append(record)
                if len(records_to_load) == 50000:
                    try:
                        db.add_all(records_to_load)
                        db.commit()
                    except Exception as e:
                        error_records.extend(records_to_load)
                        print(e)
                    records_to_load = []
            db.add_all(records_to_load)
            db.commit()


if __name__ == '__main__':
    files = TECFileReader()
    expenses = TECRecordValidation(files.expenses)
    contributions = TECRecordValidation(files.contributions)

# Base.metadata.create_all(bind=engine)
# expenses.validate(load_to_sql=True)
# contributions.validate(load_to_sql=True)
