from pathlib import Path
import csv
from dataclasses import dataclass, field
from typing import List, Dict, Callable, ClassVar, Optional, Iterator, Type, Iterable, Set, Generator, Any
from tec_validator import TECValidator, ValidationError
import sys
import os
from tqdm import tqdm
from io import BytesIO
from zipfile import ZipFile
import requests
import pandas as pd
import asyncio
import functools
import logging
import time
from collections import namedtuple
from nameparser import HumanName

logger = logging.getLogger(__name__)

tec_folder = Path.home() / 'Downloads' / "TEC_CF_CSV"

EXPENSE_FILE_COLUMNS = set()
CONTRIBUTION_FILE_COLUMNS = set()

VALIDATOR = TECValidator

STATE_CAMPAIGN_FINANCE_AGENCY = 'TEC'
EXPENSE_FILE_PREFIX = 'expend'
CONTRIBUTION_FILE_PREFIX = 'contribs'
ZIPFILE_URL = "https://www.ethics.state.tx.us/data/search/cf/TEC_CF_CSV.zip",


def timer(func: Callable) -> Callable:
    """

    :rtype: object
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"Finished {func.__name__} in {end - start:.2f} seconds")
        return result

    return wrapper


@dataclass
class TECFileReader:
    file: Path
    FILE_VALIDATOR: ClassVar[Type[TECValidator]] = VALIDATOR

    def __repr__(self):
        return f"{self.path.name}"

    def __str__(self):
        return f"{self.path.name}"

    def __post_init__(self):
        self.path: Path = field(default_factory=Path)
        self.records: Generator[Generator[Dict, Any, None]] = self.read_file()

    def read_file(self):
        with open(self.file, 'r') as f:
            yield (dict(v) for k, v in enumerate(csv.DictReader(f)))

    def validate(self):
        RecordValidation = namedtuple('RecordValidation', ['passed', 'failed'])
        valid_records, errors = [], []
        for record in self.records:
            for v in tqdm(record, desc=f'Validating {self.file.name} records'):
                try:
                    valid_records.append(TECFileReader.FILE_VALIDATOR(**v).dict())
                    # valid_records.append(valid)
                except ValidationError as e:
                    errors.append(e.json())
                    # errors.append(error)
        yield RecordValidation(valid_records, errors)


@dataclass
class TECFolderReader:
    _EXPENSE_FILE_PREFIX: str = EXPENSE_FILE_PREFIX
    _CONTRIBUTION_FILE_PREFIX: str = CONTRIBUTION_FILE_PREFIX
    _ZIPFILE_URL: str = ZIPFILE_URL

    @property
    def folder(self):
        fldr = Path.cwd()
        tmp = fldr / 'tmp'
        return tmp

    @folder.setter
    def folder(self, value):
        self.folder = value

    def __post_init__(self):

        self.expenses = TECFileGroup(
            TECFileReader(file) for file in self.folder.glob('*.csv') if file.stem.startswith(
                self._EXPENSE_FILE_PREFIX)
        )
        self.contributions = TECFileGroup(
            TECFileReader(file) for file in self.folder.glob('*.csv') if file.stem.startswith(
                self._CONTRIBUTION_FILE_PREFIX)
        )

    def download(self, read_from_temp: bool = True):
        tmp = self.folder
        temp_filename = tmp / 'TEC_CF_CSV.zip'

        def download_file() -> None:
            # download files
            with requests.get(self._ZIPFILE_URL, stream=True) as resp:
                # check header to get content length, in bytes
                total_length = int(resp.headers.get("Content-Length"))

                # Chunk download of zip file and write to temp folder
                print(f'Downloading {STATE_CAMPAIGN_FINANCE_AGENCY} Files...')
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

        def extract_zipfile():
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


@dataclass
class TECFileGroup:
    file: Generator[TECFileReader, Any, None]

    @property
    def records(self):
        return (f.read_file() for f in self.file)

    @property
    def validated(self):
        return (f.validate() for f in self.file)

    # @property
    # def failed(self):
    #     return (f.failed_validation for f in self.file)


@dataclass
class TECReportLoader:
    file: TECFileGroup
    records: List = field(init=False)
    passed: List = field(init=False)
    failed: List = field(init=False)

    @staticmethod
    def load(record_type):
        records = [r for f in record_type for r in f]
        return records

    @staticmethod
    def to_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(dataframe)

    def load_records(self):
        self.records = TECReportLoader.load(self.file.records)
        return self.records

    @timer
    def load_validated_records(self):
        _records = TECReportLoader.load(self.file.validated)
        self.passed = [record for file in _records for record in file.passed]
        self.failed = [record for file in _records for record in file.failed]
        return self

    # def load_failed_records(self):
    #     self.failed = TECReportLoader.load(self.file.failed)
    #     return self.failed


folder = TECFolderReader()
# folder.download()
expenses = TECReportLoader(folder.expenses)
contributions = TECReportLoader(folder.contributions)

expenses.load_validated_records()
# contributions.load_validated_records()

# expense_frame = pd.DataFrame.from_records(expenses.passed)