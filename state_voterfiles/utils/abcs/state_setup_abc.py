import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from icecream import ic
from functools import partial

from vep_validation_tools.utils.readers import TomlReader

from ..readers import read_csv
from ..abcs.file_loader_abc import create_headers_list, VOTERFILE_FIELD_FOLDER, VOTERFILE_RECORD_FOLDER


@dataclass
class SetupStateABC:
    """
    A class used to setup the state for processing.

    Attributes:
        state (str): The state for processing.
        data_folder (Path): The path to the data folder.
        target_folder (Path): The path to the target folder.
        voterfile_folder (Path): The path to the voterfile folder.

    Methods:
        setup_target_folder() -> Path: Sets up the target folder.
        setup_voterfile_folder() -> Path: Sets up the voterfile folder.
    """
    state: str
    city: Optional[str] = field(default=None)
    county: Optional[str] = field(default=None)
    target_example: Dict = field(init=False)
    voterfile_example: Dict = field(init=False)
    target_headers: List[str] = field(init=False)
    voterfile_headers: List[str] = field(init=False)
    target_files: Dict = field(init=False)
    voterfile_files: Dict = field(init=False)
    # _logfire = LogfireContextManager("StateSetup")
    # _logfire_span: logfire.span = None

    def __post_init__(self):
        if not self.city or self.county:
            self.voterfile_folder = VOTERFILE_RECORD_FOLDER(self.state)
        elif self.city:
            self.voterfile_folder = VOTERFILE_RECORD_FOLDER(self.state) / f'{self.state.lower()}-city-{self.city.lower()}'
        elif self.county:
            self.voterfile_folder = VOTERFILE_RECORD_FOLDER(self.state) / f'{self.state.lower()}-county-{self.county.lower()}'


    # @property
    # def logfire_span(self):
    #     # self._logfire_span = self._logfire.span(f"Setting up {self.state.title()}")
    #     return self._logfire_span

    def create_list_of_fields(self, path: Path):
        _all_file_headers = {}
        _example = None

        _file_count = len(list(path.iterdir()))
        print(_file_count)

        if _file_count == 0:
            raise FileNotFoundError(
                "No files in {state}'s {file_type} folder were found".format(
                    state=self.state.title(),
                    file_type='voterfile'
                )
            )
        # with self.logfire_span:
        #     with logfire.span(f"Reading files in {path.parent.name}"):
        for file in path.iterdir():
            _file = Path(file) if file else None
            if _file and _file.suffix not in [".csv", ".txt"]:
                print(f"Invalid file type: {_file.suffix}")

            ic("Reading file: ", _file.name)

            _file_headers = set()
            read_file = partial(read_csv, file, uppercase=True)
            if _file.suffix == ".txt":
                _delim = "\t"
                _headers_exist = TomlReader(VOTERFILE_FIELD_FOLDER(self.state)).data.get('HEADERS')
                if _headers_exist:
                    _headers = create_headers_list(_headers_exist)
                    read_file = partial(read_file, headers=_headers)
                _data = read_file(delim=_delim)
            elif _file.suffix == ".csv":
                _data = read_file()
            else:
                _data = None

            if _data:
                _example = next(_data)
                # Lowercase keys
                _all_file_headers[_file.name] = {key for key in _example.keys()}

        _headers = sorted(dict.fromkeys(headers for header_set in _all_file_headers.values() for headers in header_set))
        self.voterfile_headers = _headers
        self.voterfile_example = _example
        self.voterfile_files = _all_file_headers
        return self

    # @logfire_span_context
    def setup_all(self):
        # _span = logfire.span(f"Setting voterfile and targets for {self.state.title()}")
        for each in [self.voterfile_folder]:
            # with _span:
            self.create_list_of_fields(each)
        return self

    def setup_voterfiles(self):
        # with logfire.span(f"Setting up voterfile for {self.state.title()}"):
        self.create_list_of_fields(self.voterfile_folder)
        return self

