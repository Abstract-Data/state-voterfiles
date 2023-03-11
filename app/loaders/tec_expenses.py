from pathlib import Path
import csv
from dataclasses import dataclass, field
from typing import List, Dict, ClassVar, Type, Generator
from app.conf.config import CampaignFinanceConfig
from pydantic import ValidationError
from app.conf.tec_postgres import SessionLocal, sessionmaker, Base, engine
import os
import sys
from tqdm import tqdm
from zipfile import ZipFile
import requests
import pandas as pd
from app.conf.logger import CampaignFinanceLogger
import json

logger = CampaignFinanceLogger(__file__)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

EXPENSE_FILE_COLUMNS = set()
CONTRIBUTION_FILE_COLUMNS = set()


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
class TECRecord:
    data: Dict
    category: str = field(init=False, repr=False)
    validator: CampaignFinanceConfig.VALIDATOR = CampaignFinanceConfig.VALIDATOR
    sql_model: CampaignFinanceConfig.SQL_MODEL = CampaignFinanceConfig.SQL_MODEL

    def __post_init__(self):
        self.category = self.data[CampaignFinanceConfig.RECORD_TYPE_COLUMN]


@dataclass
class TECFile:
    file: Path
    file_name: str = field(init=False, repr=False)
    passed: List = None
    failed: List = None
    to_sql: Generator[CampaignFinanceConfig.SQL_MODEL, None, None] = field(init=False, repr=False)
    sql_model: CampaignFinanceConfig.SQL_MODEL = CampaignFinanceConfig.SQL_MODEL

    @property
    def records(self) -> Generator[TECRecord, None, None]:
        opn = open(self.file, 'r')
        for _record in csv.DictReader(opn):
            r = TECRecord(_record)
            yield r

    def load_records(self, passed_only=True) -> Dict[int, TECRecord]:
        _records = self.passed if self.passed and passed_only else self.records
        return {i: r for i, r in enumerate(_records)}

    def validate_file(self) -> [List, List]:
        _pass, _fail = [], []
        logger.info(f'Initiated record validation for {self.file_name}...')
        for record in tqdm(
                self.records,
                desc=f'Validating {self.file_name}',
                unit=' records',
                unit_scale=True,
                total=sum(1 for _ in self.records)):
            try:
                _record = record.validator(**record.data)
                _pass.append(_record)
            except ValidationError as e:
                logger.silent_error(f"RECORD VALIDATION: {e.json()}")
                _fail.append({'record': record.data, 'error': json.loads(e.json())})
        self.passed, self.failed = _pass, _fail

        _file_report = f"""\r=== File Validation Results ===
            \rState: {CampaignFinanceConfig.STATE}
            \rFile: {self.file_name}
            \rPassed: {len(self.passed):,}
            \rFailed: {len(self.failed):,}
            \rPass %: {round(len(self.passed) / (len(self.passed) + len(self.failed)) * 100, 2)}%
            """
        logger.info(_file_report)
        return self.passed, self.failed

    def generate_models(self) -> CampaignFinanceConfig.SQL_MODEL:
        logger.info(f'Creating {self.file_name} SQL models...')
        for _record in tqdm(self.passed, desc=f'Creating {self.file_name} SQL models', unit=' records'):
            self.to_sql = yield TECFile.sql_model(**_record.dict())

    def __post_init__(self):
        self.file_name = self.file.name


@dataclass
class TECCategory:
    category: Generator[Path, None, None]
    passed: Dict = field(init=False, repr=False)
    failed: Dict = field(init=False, repr=False)
    records: List = field(init=False, repr=False)
    sql_models: List = field(init=False, repr=False)

    def __post_init__(self):
        self.files = TECCategory.read_files(self.category)

    @classmethod
    def read_files(cls, cat) -> Generator[TECFile, None, None]:
        for file in cat:
            reader = TECFile(file)
            yield reader

        logger.info(f"{len(cat.__str__())} files loaded, turned into TECFile objects")

    def load_files(self):
        _files = []
        for _file in tqdm(self.files, desc=f'Loading files', unit=' files'):
            _files.append(_file.load_records())

        self.records = _files
        return self.records

    def load_records(self, passed_only=True):
        _records = []
        for _file in tqdm(self.files, desc=f'Loading records', unit=' records'):
            _file = _file.load_records(passed_only=passed_only)
            for _each in _file:
                _records.append(_file[_each])

        self.records = _records
        return self.records

    def validate(self, load_to_sql: bool = False) -> [Dict, Dict]:
        logger.info(f'Initiated category validation...Load to SQL: {load_to_sql}')
        self.passed, self.failed = {}, {}
        for _file in self.files:
            _passed, _failed = _file.validate_file()
            self.passed.update({_file.file_name: _passed})
            self.failed.update({_file.file_name: _failed})

            if load_to_sql:
                _models = _file.generate_models()
                TECCategory.load_file_to_sql(models=_models)

        def result_report(_pass=None, _fail=None) -> None:
            if not all([_pass, _fail]):
                _fail, _pass = self.failed, self.passed
            result_summary = f"""
            ============== CATEGORY VALIDATION SUMMERY ============"""
            _file_results = [(len(_pass.keys()), sum(len(l) for l in _pass), sum(len(l) for l in _fail))]
            result_summary_table = pd.DataFrame(
                _file_results,
                columns=[
                    'Files', 'Passed', 'Failed'
                ]
            ).to_markdown(index=False)

            results_per_file_header = f"""
            ============== CATEGORY VALIDATION PER-FILE ============"""
            file_report = []
            for _file_failed, _failed_ in _fail.items():
                for _file_passed, _passed_ in _pass.items():
                    if _file_failed == _file_passed:
                        file_report.append(
                            (
                                _file_passed,
                                f"{len(_passed_):,}",
                                f"{len(_failed_):,}"
                            )
                        )
            logger.info(f"""
            {result_summary}
            \r\t\t{result_summary_table}
            """)

            logger.info(f"""
            {results_per_file_header}""")
            logger.info(
                f"""{pd.DataFrame(file_report, columns=['File', 'Passed', 'Failed']).to_markdown(index=False)}""")

        result_report()
        return self.passed, self.failed

    @classmethod
    def load_file_to_sql(cls, models: Generator, session: sessionmaker = SessionLocal):
        error_records = []
        records_to_load = []
        _loaded_counter = 0
        with session() as db:
            logger.info(f"Loading records to SQL")
            for record in models:
                records_to_load.append(record)
                if len(records_to_load) == 50000:
                    try:
                        db.add_all(records_to_load)
                        db.commit()
                        _loaded_counter += len(records_to_load)
                    except Exception as e:
                        error_records.extend(records_to_load)
                        logger.error(e)
                    records_to_load = []
            db.add_all(records_to_load)
            db.commit()
            _loaded_counter += len(records_to_load)
        logger.info(f"Loaded {_loaded_counter} records to SQL successfully")
        logger.info(f"Loaded {_loaded_counter} records to SQL")


@dataclass
class TECFolderLoader:
    """
    TECFolderReader
    ===============
    This class is used to pull Campaign finance files from the TEC website.
    It is used to download the files from the TEC website and
    validate the data in the files.
    """

    folder: ClassVar[Path] = Path.cwd() / 'tmp'
    _ZIPFILE_URL: ClassVar[str] = CampaignFinanceConfig.ZIPFILE_URL
    expenses: ClassVar[TECCategory] = None
    contributions: ClassVar[TECCategory] = None

    def __post_init__(self):
        TECFolderLoader.expenses = TECCategory(TECFolderLoader.file_list(CampaignFinanceConfig.EXPENSE_FILE_PREFIX))
        TECFolderLoader.contributions = TECCategory(
            TECFolderLoader.file_list(CampaignFinanceConfig.CONTRIBUTION_FILE_PREFIX))

    @classmethod
    def file_list(cls, prefix) -> Generator[Path, None, None]:
        if not cls.folder.exists():
            err_msg = FileNotFoundError(f'Folder {cls.folder} does not exist')
            logger.warning(err_msg)
            raise err_msg

        for f in cls.folder.glob(f'{prefix}*'):
            yield Path(f)
        logger.info(f'Found {len(list(cls.folder.glob(f"{prefix}*")))} files with prefix {prefix}')

    @classmethod
    def download(cls, read_from_temp: bool = True) -> Path or object:
        tmp = cls.folder
        temp_filename = tmp / 'TEC_CF_CSV.zip'

        def download_file() -> None:
            # download files
            with requests.get(cls._ZIPFILE_URL, stream=True) as resp:
                logger.info(f'Initiated {CampaignFinanceConfig.STATE_CAMPAIGN_FINANCE_AGENCY} file download...')
                # check header to get content length, in bytes
                total_length = int(resp.headers.get("Content-Length"))

                # Chunk download of zip file and write to temp folder
                with open(temp_filename, 'wb') as f:
                    for chunk in tqdm(resp.iter_content(
                            chunk_size=1024),
                            total=round(total_length / 1024, 2),
                            unit='KB',
                            desc='Downloading'):
                        if chunk:
                            f.write(chunk)
                    logger.info(f'Download Complete. File saved to {temp_filename}')
                return None

        def extract_zipfile() -> None:
            # extract zip file to temp folder
            with ZipFile(temp_filename, 'r') as myzip:
                logger.info(f'Extracting {CampaignFinanceConfig.STATE_CAMPAIGN_FINANCE_AGENCY} Files...')
                for _ in tqdm(myzip.namelist()):
                    myzip.extractall(tmp)
                os.unlink(temp_filename)
                cls.folder = tmp  # set folder to temp folder
                logger.info(f'Files extracted to {tmp}')

        try:

            if read_from_temp is False:
                # check if tmp folder exists
                if tmp.is_dir():
                    logger.info(f'Temp folder already exists.')
                    ask_to_make_folder = input("Temp folder already exists. Overwrite? (y/n): ")
                    if ask_to_make_folder.lower() == 'y':
                        logger.info("User opted to overwrite temp folder.")
                        download_file()
                        extract_zipfile()
                    else:
                        as_to_change_folder = input("Use temp folder as source? (y/n): ")
                        if as_to_change_folder.lower() == 'y':
                            if tmp.glob('*.csv') == 0 and tmp.glob('*.zip') == 1:
                                logger.warning('No CSV files in temp folder. Found .zip file...')
                                logger.info('Extracting .zip file...')
                                extract_zipfile()
                            else:
                                cls.folder = tmp  # set folder to temp folder
                            return cls
                        else:
                            logger.info('Exiting...')
                            sys.exit()

            else:
                cls.folder = tmp  # set folder to temp folder

        # remove tmp folder if user cancels download
        except KeyboardInterrupt:
            logger.debug('Download Cancelled')

            for file in tmp.iterdir():
                file.unlink()
            logger.debug('Temp files in temp folder removed')
            tmp.rmdir()
            logger.debug('Temp folder removed')
            print('Temp Folder Removed')

            return cls


Base.metadata.create_all(bind=engine)
files = TECFolderLoader()
expenses = files.expenses.validate(load_to_sql=True)
contributions = files.contributions.validate(load_to_sql=True)

