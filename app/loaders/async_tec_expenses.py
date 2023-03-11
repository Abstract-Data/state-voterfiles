import csv
from dataclasses import dataclass, field
from typing import List, Dict, ClassVar, Type, Generator, AsyncGenerator, AsyncIterable, AsyncIterator, Callable, Any, \
    Coroutine
from app.conf.config import CampaignFinanceConfig
from pydantic import ValidationError
from app.conf.tec_postgres import SessionLocal, sessionmaker, Base, engine
import os
import sys
from tqdm import tqdm
from zipfile import ZipFile
import requests
import pandas as pd
import logging
import asyncio
from aiopath import AsyncPath as Path

logger = logging.getLogger(__name__)

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


"""
====================
ASYNC FUNCTIONS
====================
"""


async def get_folder() -> Path:
    fldr = Path.cwd().parent.parent
    tmp = fldr / 'tmp'
    await asyncio.sleep(1)
    return tmp


async def file_list(prefix) -> AsyncGenerator[Path, None]:
    folder = await get_folder()
    # Return a list of files that match the prefix as a coroutine
    async for file in folder.glob(f'{prefix}*'):
        yield file


async def get_records(file) -> Generator[Dict, None]:
    async with open(file, 'r') as f:
        return csv.DictReader(f)


async def main():
    expense_files = asyncio.create_task(file_list(prefix=CampaignFinanceConfig.EXPENSE_FILE_PREFIX))
    contribution_files = asyncio.create_task(file_list(prefix=CampaignFinanceConfig.CONTRIBUTION_FILE_PREFIX))
    expense_paths = await expense_files
    contribution_paths = await contribution_files
    contribution_records = asyncio.gather(*[get_records(file) async for file in contribution_paths])
    return expense_paths, contribution_paths, contribution_records

test_expense, test_contributions, test_contribution_records = asyncio.run(main())


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
    expenses: Generator[Path, None, None] = field(default_factory=list)
    contributions: Generator[Path, None, None] = field(default_factory=list)

    async def __aenter__(self) -> 'TECFolderLoader':
        return self

    @property
    def folder(self) -> Path:
        fldr = Path.cwd().parent.parent
        tmp = fldr / 'tmp'
        return tmp

    @folder.setter
    def folder(self, value) -> None:
        self.folder = value

    async def file_list(self, prefix) -> AsyncGenerator[Path, None]:
        if not self.folder.exists():
            raise FileNotFoundError(f'Folder {self.folder} does not exist')

        for f in self.folder.glob(f'{prefix}*'):
            path = Path(f)
            yield path

    def download(self, read_from_temp: bool = True) -> Path or object:
        # TODO: Make function async
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
        self.expenses = self.file_list(self._EXPENSE_FILE_PREFIX)
        self.contributions = self.file_list(self._CONTRIBUTION_FILE_PREFIX)


@dataclass
class TECRecord:
    record: Dict
    category: str = field(init=False, repr=False)
    validator: CampaignFinanceConfig.VALIDATOR = field(init=False, repr=False)
    sql_model: CampaignFinanceConfig.SQL_MODEL = field(init=False, repr=False)

    def __post_init__(self):
        self.category = self.record[CampaignFinanceConfig.RECORD_TYPE_COLUMN]


@dataclass
class TECFile:
    file: Path
    file_name: str = field(init=False, repr=False)
    records: AsyncGenerator | Coroutine = field(init=False, repr=False)
    passed: List = field(init=False, repr=False)
    failed: List = field(init=False, repr=False)
    sql_models: Generator[CampaignFinanceConfig.SQL_MODEL, None, None] = field(init=False, repr=False)

    async def __aenter__(self) -> 'TECFile':
        return self

    def __await__(self):
        return self.get_records().__await__()

    def __post_init__(self):
        self.file_name = self.file.name
        # self.records = self.load_records()

    async def get_records(self) -> TECRecord:
        async with open(self.file, 'r') as f:
            reader = csv.DictReader(f)
            for record in reader:
                yield TECRecord(record)

    async def load_records(self, passed_only=True) -> Dict[int, TECRecord]:
        _records = self.passed if self.passed and not passed_only else self.get_records()
        return {i: r for i, r in enumerate(_records)}

    async def validate_file(self) -> [List, List]:
        _pass, _fail = [], []
        for record in tqdm(self.records, desc=f'Validating {self.file_name}', unit=' records'):
            try:
                _record = CampaignFinanceConfig.VALIDATOR(**record.record)
                _pass.append(_record)
            except ValidationError as e:
                _fail.append({'record': record.record, 'error': e})
        self.passed, self.failed = _pass, _fail
        sys.stdout.write(
            f"""\r=== File Validation Results ===
            \rState: {CampaignFinanceConfig.STATE}
            \rFile: {self.file_name}
            \rPassed: {len(self.passed):,}
            \rFailed: {len(self.failed):,}
            \rPass %: {round(len(self.passed) / (len(self.passed) + len(self.failed)) * 100, 2)}%
            """)
        sys.stdout.flush()
        return self.passed, self.failed

    def generate_models(self) -> CampaignFinanceConfig.SQL_MODEL:
        for _record in tqdm(self.passed, desc=f'Creating {self.file_name} SQL models', unit=' records'):
            self.sql_models = yield CampaignFinanceConfig.SQL_MODEL(**_record.dict())

    def __post_init__(self):
        self.file_name = self.file.name


@dataclass
class TECCategory:
    """
    TECCategory
    =============
    This class is used to read TEC campaign finance files.
    It is used to read the files from the TEC website and
    validate the data in the files.
    """

    category_files: TECFolderLoader = TECFolderLoader()
    category: ClassVar[Type[CampaignFinanceConfig.RECORD_CATEGORY_TUPLE]] = CampaignFinanceConfig.RECORD_CATEGORY_TUPLE
    FILE_VALIDATOR: ClassVar[Type[CampaignFinanceConfig.VALIDATOR]] = CampaignFinanceConfig.VALIDATOR

    @staticmethod
    async def read_files(file_list: category) -> AsyncGenerator[TECRecord, None]:
        async for file in file_list:
            reader = TECFile(file)
            yield await reader

    @staticmethod
    async def load_records(list_name: category) -> List[TECRecord]:
        records = {}
        async for each in list_name.records:
            records[each.fileName] = [i for i in each.fileRecord]
        await asyncio.sleep(0)
        return [
            each for record in records.values() for each in tqdm(
                record,
                desc=f'Loading Records from {record[0].file_name}',
                unit=' records'
            )
        ]

    @staticmethod
    async def file_loader(kind, category_type) -> List[TECRecord]:
        category = TECCategory.category(
            kind=kind,
            records=TECCategory.read_files(category_type))
        return await TECCategory.load_records(category)

    async def main(self):
        get_contributions = asyncio.create_task(self.file_loader('contributions', self.category_files.contributions))
        get_expenses = asyncio.create_task(self.file_loader('expenses', self.category_files.expenses))
        await asyncio.gather(get_contributions, get_expenses)
        return self

    def __post_init__(self):
        self.path: Path = field(default_factory=Path)
        asyncio.run(self.main())

        # self.contributions: TECCategory.category = TECCategory.category(
        #     kind='contribution',
        #     records=TECCategory.read_files(self.category_files.contributions)
        # )
        # 
        # self.expenses: TECCategory.category = TECCategory.category(
        #     kind='expenses',
        #     records=TECCategory.read_files(self.category_files.expenses)
        # )


@dataclass
class TECRecordValidation:
    """
    TECRecordValidation
    ===================
    This class is used to validate the TEC campaign finance data.
    """
    filesCategory: TECCategory.category
    passed: Dict = field(init=False)
    failed: Dict = field(init=False)
    _record_cateogry: str = field(init=False)
    _record_types: Dict[str, str] = field(init=False)

    @property
    def records(self) -> Generator[TECRecord, None, None]:
        for _record in self.filesCategory.records:
            yield _record

    @property
    def record_category(self):
        return self.filesCategory.file_name

    def validate(self, load_to_sql: bool = False) -> [Dict, Dict]:
        self.passed, self.failed = {}, {}
        for _file in self.filesCategory.records:
            _passed, _failed = _file.validate_file()
            self.passed.update({_file.file_name: _passed})
            self.failed.update({_file.file_name: _failed})

            if load_to_sql:
                _models = _file.create_sql_models()
                TECRecordValidation.load_file_to_sql(models=_models)

        def result_report(_pass=None, _fail=None) -> None:
            if not all([_pass, _fail]):
                _fail, _pass = self.failed, self.passed
            result_summary = f"""
            ============== {self.filesCategory.kind.upper()} CATEGORY VALIDATION SUMMERY ============"""
            _file_results = [(len(_pass.keys()), sum(len(l) for l in _pass), sum(len(l) for l in _fail))]
            result_summary_table = pd.DataFrame(_file_results, columns=['Files', 'Passed', 'Failed']).to_markdown()

            results_per_file_header = f"""
            ============== {self.filesCategory.kind.upper()} CATEGORY VALIDATION PER-FILE ============"""
            file_report = []
            for _file_failed, _failed_ in _fail.items():
                for _file_passed, _passed_ in _fail.items():
                    if _file_failed == _file_passed:
                        file_report.append(
                            [(_file_passed, sum(len(l) for l in _passed_), sum(len(l) for l in _failed_))])
            print(result_summary)
            print(result_summary_table)
            print(results_per_file_header)
            print(pd.DataFrame(file_report, columns=['File', 'Passed', 'Failed']).to_markdown())

        result_report()
        return self.passed, self.failed

    @classmethod
    def load_file_to_sql(cls, models: Generator, session: sessionmaker = SessionLocal):
        error_records = []
        records_to_load = []
        _loaded_counter = 0
        with session() as db:
            for record in models:
                records_to_load.append(record)
                if len(records_to_load) == 50000:
                    try:
                        db.add_all(records_to_load)
                        db.commit()
                        _loaded_counter += len(records_to_load)
                    except Exception as e:
                        error_records.extend(records_to_load)
                        print(e)
                    records_to_load = []
            db.add_all(records_to_load)
            db.commit()
            _loaded_counter += len(records_to_load)
        print(f"Loaded {_loaded_counter} records to SQL")


# files = TECCategory()
# expenses = TECRecordValidation(files.expenses)
# expenses.validate()
# contributions = TECRecordValidation(files.contributions)

# Base.metadata.create_all(bind=engine)
# expenses.validate()

# contributions.validate(load_to_sql=True)

# if __name__ == '__main__':
#     files = TECCategory()
#     expenses = TECRecordValidation(files.expenses)
#     contributions = TECRecordValidation(files.contributions)
