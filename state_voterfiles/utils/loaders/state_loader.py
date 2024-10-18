from typing import Any, Generator, Dict, Type
from functools import partial
from dataclasses import dataclass
from pathlib import Path

from state_voterfiles.utils.readers.toml_reader import TomlReader
from state_voterfiles.utils.abcs.folder_reader_abc import FolderReaderABC
from state_voterfiles.utils.abcs.file_loader_abc import (
    FileTypeConfigsABC,
    FileLoaderABC,
    VOTERFILE_FIELD_FOLDER,
    VOTERFILE_RECORD_FOLDER,
)
from state_voterfiles.utils.db_models.record import RecordBaseModel
from state_voterfiles.utils.funcs.csv_export import CSVExport
from state_voterfiles.utils.abcs.state_setup_abc import SetupStateABC
from state_voterfiles.utils.new_create_validator import CreateValidator


class SetupState(SetupStateABC):
    pass


class StateFolderReader(FolderReaderABC):
    pass


class StateVoterFileConfigs(FileTypeConfigsABC):
    pass


# class VoterFileRecord(RecordBaseModel):
#     # TODO: Modify this so that I can use RecordModel and just change the table name instead of inheriting from RecordBaseModel
#     pass


@dataclass
class StateVoterFile(FileLoaderABC):
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
    data: Any = None
    _config: partial[StateVoterFileConfigs] = partial(
        StateVoterFileConfigs,
        field_file_lambda=VOTERFILE_FIELD_FOLDER,
        record_folder_lambda=VOTERFILE_RECORD_FOLDER
    )

    def __repr__(self):
        """Returns a string representation of the state voter file."""
        return f"{self.state.title()} Voter File"

    def __post_init__(self):
        RecordBaseModel.__tablename__ = "voterfile"
        self.validation = CreateValidator(
            state_name=(self.state, 'voterfiles'),
            record_validator=RecordBaseModel,
            renaming_validator=self.config.renaming_model
        )

    def combine_and_export(self, records: Generator[Dict[str, Any], None, None] = None) -> CSVExport:
        _file_name = f"{self.state.lower()}_combined_voterfile"
        _path = self.config.folder.folder_path
        _data = records if records else self.data
        self.logger.info(f"Combining all {self.state.title()} voter files to {_path.name}")
        return CSVExport(
            data=_data,
            name=_file_name,
            path=_path
        ).export()


