from __future__ import annotations
from typing import Any, Generator, Dict, Annotated, Optional, Callable, Iterable
import abc
from functools import partial, wraps, cached_property
import contextlib
from dataclasses import dataclass, field
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm
from pydantic import BaseModel, Field as PydanticField
# import logfire


from state_voterfiles.utils.create_validator import CreateValidator
from state_voterfiles.utils.readers.csv_reader import read_csv
from state_voterfiles.utils.funcs.csv_export import CSVExport
from state_voterfiles.utils.readers.toml_reader import TomlReader
from state_voterfiles.utils.abcs.folder_reader_abc import FolderReaderABC
from state_voterfiles.utils.pydantic_models.rename_model import create_renamed_model
# from state_voterfiles.utils.logger import Logger

# logfire.configure()

TEMP_DATA = TomlReader(file=Path(__file__).parents[2] / "folder_paths.toml")

USE_VEP_FILES = False
DATA_FOLDER = Path("/Users/johneakin/PyCharmProjects/vep-2024/data/voterfiles")

FIELD_FOLDER = Path(__file__).parents[2] / "field_references" / "states"


def VOTERFILE_FIELD_FOLDER(state: str, county: str = None) -> Path:
    folder = FIELD_FOLDER / (_state := str(state).lower())
    if not county:
        return folder / f"{_state}-fields.toml"
    else:
        return folder / f"{_state}-{county.lower()}.toml"


def VOTERFILE_RECORD_FOLDER(state: str) -> Path:
    return DATA_FOLDER / str(state).lower()


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


class FileTypeConfigs(BaseModel, abc.ABC):
    state: Annotated[str, PydanticField(description="The state for which the file is being processed.")]
    field_file_lambda: Callable[[str], Path]
    record_folder_lambda: Callable[[str], Path]
    _field_file_path: Annotated[Path, PydanticField(default=None)]
    _fields: Annotated[Optional[TomlReader], PydanticField(default=None)]
    _headers: Annotated[Optional[list], PydanticField(default=None)]
    _folder: Annotated[Optional[FolderReaderABC], PydanticField(default=None)]
    _renaming_model: Annotated[Optional[create_renamed_model], PydanticField(default=None)]

    @property
    def field_file_path(self):
        self._field_file_path = self.field_file_lambda(self.state)
        return self._field_file_path

    @property
    def fields(self):
        self._fields = TomlReader(
            file=self.field_file_path
        )
        return self._fields

    @property
    def headers(self):
        _headers = self.fields.data.get(
            'HEADERS'
        )
        if _headers:
            self._headers = create_headers_list(
                _headers
            )
            return self._headers

    @property
    def folder(self):
        _record_folder = self.record_folder_lambda(self.state)
        self._folder = FolderReaderABC(
            state=self.state,
            file_type="targets" if "targets" in str(_record_folder) else "voterfiles",
            folder_path=_record_folder
        ).read()
        return self._folder

    @property
    def renaming_model(self):
        _model = create_renamed_model(
            state=self.state,
            field_path=self.fields.file
        )
        self._renaming_model = _model
        return self._renaming_model


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
    _config: partial[FileTypeConfigs] = None
    data: Any = None
    fields: TomlReader = None
    context_managers: list = field(default_factory=list)
    _validation: CreateValidator = None
    _folder: FolderReaderABC = None
    _newest_file: Path = None
    _read_all_files: bool = False

    @abc.abstractmethod
    def __post_init__(self):
        self.validation = ...

    def __init__(self, *args, **kwargs):
        # Initialize the context immediately
        self.context_managers.append(f"{self.__class__.__name__} for {self.state.title()}")

        # Call the default __post_init__ if necessary
        self.__post_init__()

        # Now proceed with any other initialization tasks you might have
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """Returns a string representation of the state voter file."""
        return f"{self.state.title()} Voter File"

    @contextlib.contextmanager
    def context_manager_stack(self, context_managers):
        """
        A context manager that manages multiple context managers using ExitStack.

        Parameters:
        context_managers (list): A list of context manager instances to be managed.
        """
        with contextlib.ExitStack() as stack:
            for cm in context_managers:
                stack.enter_context(cm)
            yield stack

    @cached_property
    def config(self):
        return self._config(state=self.state)

    @cached_property
    def logger(self):
        """Returns a logger instance with the module name set to 'StateFileFunctions'."""
        return None

    @property
    def validation(self):
        return self._validation

    @validation.setter
    def validation(self, value):
        self._validation = value

    @validation.getter
    def validation(self):
        return self._validation

    def validate(self, records: Iterable[Dict[str, Any]] = None) -> CreateValidator:
        """Validates the voter file records and returns the validation instance."""
        # self.context_managers.append(
        #     logfire.span(f"Validating {self.__class__.__name__} records for {self.state.title()}"))
        # logfire.info(f"Validating {self.__class__.__name__} records for {self.state.title()}")
        with self.context_manager_stack(self.context_managers):
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
        if self.config.folder.newest_file.suffix == '.txt':
            _headers = self.config.headers
            if _headers:
                _kwargs["headers"] = _headers
        if uppercase:
            _kwargs["uppercase"] = uppercase
        if lowercase:
            _kwargs["lowercase"] = lowercase

        if file_path:
            # logfire.info(f"Reading single file: {file_path.name}")
            # with self.context_manager_stack(self.context_managers):
            data = read_one_file_func(
                folder=file_path,
                **_kwargs
            ) if _kwargs else read_one_file_func(
                folder=file_path
            )
            return data
        elif self._read_all_files:
            # logfire.info(f"Reading all files for {self.state.title()}")
            _data = read_all_files_func(
                folder=self.config.folder.files,
                **_kwargs
            ) if _kwargs else read_all_files_func(
                folder=(file for file in self.config.folder.files if 'combined' not in file.name)
            )

        else:
            # logfire.info(f"Reading newest file for {self.state.title()}")
            _data = read_one_file_func(
                folder=self.config.folder.newest_file,
                **_kwargs
            ) if _kwargs else read_one_file_func(
                folder=self.config.folder.newest_file,
                **_kwargs
            )
        self.data = _data
        return self.data

    def load(self) -> list[dict]:
        if not self.data:
            self.read()
        # self.context_managers.append(logfire.span(f"Loading {self.state.title()} voter file"))
        with self.context_manager_stack(self.context_managers):
            return list(self.data)

    # def combine_and_export(self, records: Generator[Dict[str, Any], None, None] = None) -> CSVExport:
    #     _file_name = f"{self.state.lower()}_combined_voterfile"
    #     _path = self.config.folder.folder_path
    #     _data = records if records else self.data
    #     self.logger.info(f"Combining all {self.state.title()} voter files to {_path.name}")
    #     return CSVExport(
    #         data=_data,
    #         name=_file_name,
    #         path=_path
    #     ).export()
