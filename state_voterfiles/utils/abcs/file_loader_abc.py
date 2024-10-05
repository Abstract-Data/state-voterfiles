from __future__ import annotations
from typing import Any, Generator, Dict, Annotated, Optional, Callable, Iterable, ClassVar
import abc
from functools import partial, wraps, cached_property
import contextlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import field, dataclass

from tqdm import tqdm
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import BaseModel, Field as PydanticField, DirectoryPath, FilePath, ConfigDict
# import logfire


from state_voterfiles.utils.new_create_validator import CreateValidator
from state_voterfiles.utils.readers.csv_reader import read_csv
from state_voterfiles.utils.readers.toml_reader import TomlReader
from state_voterfiles.utils.funcs import CSVExport
from state_voterfiles.utils.abcs.folder_reader_abc import FolderReaderABC
from state_voterfiles.utils.pydantic_models.rename_model import create_renamed_model
# from state_voterfiles.utils.logger import Logger

# logfire.configure()

TEMP_DATA = TomlReader(file=Path(__file__).parents[2] / "folder_paths.toml")

USE_VEP_FILES = True
PACKAGE_DATA_FOLDER = Path(__file__).parents[3] / "data"

DATA_FOLDER = Path("/Users/johneakin/PyCharmProjects/vep-2024/data") if USE_VEP_FILES else PACKAGE_DATA_FOLDER

FIELD_FOLDER = Path(__file__).parents[2] / "field_references" / "states"


def VOTERFILE_FIELD_FOLDER(state: str, county: str = None, city: str = None) -> Path:
    folder = FIELD_FOLDER / (_state := str(state).lower())
    if county:
        return folder / f"{_state}-county-{county.lower()}.toml"
    elif city:
        return folder / f"{_state}-city-{city.lower()}.toml"
    else:
        return folder / f"{_state}-fields.toml"


def VOTERFILE_RECORD_FOLDER(state: str, county: str = None, city: str = None) -> Path:
    data_folder = DATA_FOLDER / str(state).lower()
    if city:
        data_folder = data_folder / f"{state.lower()}-city-{city.lower()}"
    elif county:
        data_folder = data_folder / f"{state.lower()}-county-{county.lower()}"
    else:
        data_folder
    return data_folder


def logfire_wrapper(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Create a logfire span with a name based on the class and state
        # with logfire.span(f"{self.__class__.__name__} for {self.state.title()}"):
        return func(self, *args, **kwargs)

    return wrapper


def logfire_class_wrapper(cls):
    """
    A class decorator that wraps all methods of the class with logfire_wrapper.
    """
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("__"):
            wrapped_method = logfire_wrapper(attr_value)
            setattr(cls, attr_name, wrapped_method)
    return cls


# def logfire_class_wrapper(cls):
#     for attr_name, attr_value in cls.__dict__.items():
#         if callable(attr_value) and not attr_name.startswith("__") and attr_name in ["validate", "read"]:
#             setattr(cls, attr_name, logfire_span(attr_value))
#     return cls


def create_headers_list(headers: dict):
    # Convert the headers dictionary to a list of header names
    return [value for key, value in sorted(headers.items(), key=lambda item: int(item[0]))]


def read_all_files_func(
        folder, **kwargs) -> Generator[Dict, None, None]:
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(read_csv, file, **kwargs): file for file in folder
        }
        for future in as_completed(futures):
            yield from future.result()


def read_one_file_func(folder: Path, **kwargs) -> Generator[Dict, None, None]:
    for record in tqdm(read_csv(folder, **kwargs), desc=f"Reading {folder.name}", unit=" records"):
        yield record


@dataclass
class FileTypeConfigsABC(abc.ABC):
    file_type: ClassVar[str]
    folder: FolderReaderABC
    file_loader: FileLoaderABC
    renaming_model: Optional[create_renamed_model] = field(default=None)
    fields: Optional[TomlReader] = field(default=None)
    headers: list = field(default=None, init=False)
    _field_file_path: Path = field(default=None)
    _record_file_path: Path = field(default=None)

    def __post_init__(self):
        self.fields = TomlReader(
            file=self.field_file_path
        )
        self.renaming_model = create_renamed_model(
            state=self.file_loader.state,
            field_path=self.fields.file if self.fields else None
        )
        self.folder = self.folder(
            state=self.file_loader.state,
            file_type=self.file_type,
            folder_path=self.record_file_path
        ).read()
        if _headers := self.fields.data.get('HEADERS'):
            self.headers = _headers

    @property
    @abc.abstractmethod
    def field_file_path(self):
        folder = FIELD_FOLDER / (state := str(self.file_loader.state).lower())
        if county := self.file_loader.county:
             p = folder / f"{state}-county-{county.lower()}.toml"
        elif city := self.file_loader.city:
             p = folder / f"{state}-city-{city.lower()}.toml"
        else:
             p = folder / f"{state}-fields.toml"
        self._field_file_path = p
        return self._field_file_path

    @property
    @abc.abstractmethod
    def record_file_path(self) -> Path:
        data_folder = DATA_FOLDER / self.file_type / (state := str(self.file_loader.state).lower())
        if city := self.file_loader.city:
            data_folder = data_folder / f"{state}-city-{city.lower()}"
        elif county := self.file_loader.county:
            data_folder = data_folder / f"{state}-county-{county.lower()}"

        self._record_file_path = data_folder
        return self._record_file_path


@dataclass
class FileLoaderABC(abc.ABC):
    """
    An abstract base class used to define the methods for a state voter file loader.

    Attributes
    ----------
    state : str
        The state for which the voter file is being processed.
    data : Any
        The data reader instance for reading the voter file.
    fields : TomlReader
        The Toml reader instance for reading the field configuration.
    _validation : CreateValidator
        The validator instance for validating the voter file records.
    _folder : FolderReader
        The folder reader instance for reading the folder containing the voter files.
    _newest_file : Path
        The path to the newest file in the folder.

    Methods
    -------
    validate()
        Validates the voter file records and returns the validation instance.
    read_file(file: Path = None)
        Reads the voter file and returns a data reader instance.

    Properties
    ----------
    logger
        Returns a logger instance with the module name set to 'StateFileFunctions'.
    folder
        Returns a folder reader instance for the state voter files.
    """

    state: str
    county: Optional[str] = field(default=None)
    city: Optional[str] = field(default=None)
    config: FileTypeConfigsABC = None
    data: Any = None
    fields: TomlReader = None
    # context_managers: list = field(default_factory=list)
    validation: CreateValidator = None
    _newest_file: FilePath = None
    _read_all_files: bool = False

    @abc.abstractmethod
    def __init__(self):
        self.config = ...
        self.validation = ...

    def __repr__(self):
        """Returns a string representation of the state voter file."""
        return f"{self.state.title()} Voter File"

    # @contextlib.contextmanager
    # def context_manager_stack(self, context_managers):
    #     """
    #     A context manager that manages multiple context managers using ExitStack.
    #
    #     Parameters:
    #     context_managers (list): A list of context manager instances to be managed.
    #     """
    #     with contextlib.ExitStack() as stack:
    #         for cm in context_managers:
    #             stack.enter_context(cm)
    #         yield stack
    @cached_property
    def logger(self):
        """Returns a logger instance with the module name set to 'StateFileFunctions'."""
        return None

    def validate(self, records: Iterable[Dict[str, Any]] = None, **kwargs) -> CreateValidator:
        """Validates the voter file records and returns the validation instance."""
        # self.context_managers.append(
        #     logfire.span(f"Validating {self.__class__.__name__} records for {self.state.title()}"))
        # logfire.info(f"Validating {self.__class__.__name__} records for {self.state.title()}")
        # with self.context_manager_stack(self.context_managers):
        if records:
            self.validation.run_validation(
                records=records,
            )
        else:
            self.validation.run_validation(self.data)
        return self.validation

    def read_all_files(self) -> FileLoaderABC:
        self._read_all_files = True
        return self

    def read_newest_file(self):
        self._read_all_files = False
        return self

    def read(self, file_path: Path = None, uppercase: bool = True, lowercase: bool = None) -> Any:
        """Reads the voter file and returns a data reader instance."""
        _kwargs = {}
        # if self.config.folder and self.config.folder.newest_file.suffix == '.txt':
        #     _kwargs["headers"] = _headers if (_headers := self.config.headers) else None
        # _kwargs["uppercase"] = uppercase if uppercase else False
        # _kwargs["lowercase"] = lowercase if lowercase else False

        if file_path:
            # logfire.info(f"Reading single file: {file_path.name}")
            # with self.context_manager_stack(self.context_managers):
            data = read_one_file_func(folder=file_path, **_kwargs) if _kwargs else read_one_file_func(folder=file_path)
            return data

        elif self._read_all_files:
            # logfire.info(f"Reading all files for {self.state.title()}")
            _data = read_all_files_func(folder=self.config.folder.files, **_kwargs) \
                if _kwargs else read_all_files_func(
                folder=(file for file in self.config.folder.files if 'combined' not in file.name))

        else:
            # logfire.info(f"Reading newest file for {self.state.title()}")
            _data = read_one_file_func(folder=self.config.folder.newest_file, **_kwargs) \
                if _kwargs else read_one_file_func(folder=self.config.folder.newest_file, **_kwargs)
        self.data = _data
        return self.data

    def load(self) -> list[dict]:
        if not self.data:
            self.read()
        # self.context_managers.append(logfire.span(f"Loading {self.state.title()} voter file"))
        # with self.context_manager_stack(self.context_managers):
        return list(self.data)
