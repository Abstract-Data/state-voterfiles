import abc
from pathlib import Path
from dataclasses import dataclass, field
from typing import List
import asyncio
from functools import cached_property

# from state_voterfiles.utils.logger import Logger


@dataclass
class FolderReaderABC(abc.ABC):
    """
    A class used to read files from a specified folder.

    Attributes:
        state (str): The state of the reader.
        file_type (str): The type of file to read.
        folder_path (Path): The path to the folder to read files from.
        _csv_files (List[Path]): A list of CSV files in the folder.
        _file_list (List[Path]): A list of files in the folder.
        _newest_file (Path): The newest file in the folder.

    Properties:
        logger (Logger): Returns an instance of the Logger class.
        csv_files (List[Path]): Returns a list of CSV files in the folder. Can also set the list of CSV files.
        newest_file (Path): Returns the newest file in the folder. Can also set the newest file.

    Methods:
        async_csv_files() -> List[Path]: Asynchronously returns a list of CSV files in the folder.
        async_newest_file(): Asynchronously returns the newest file in the folder.
        read(): Reads the CSV files and the newest file in the folder.
    """
    state: str
    file_type: str
    folder_path: Path
    _files: List[Path] = field(default_factory=list, init=False)
    _newest_file: Path = field(default_factory=Path, init=False)
    _files_need_update: bool = field(default=True, init=False)
    _newest_file_need_update: bool = field(default=True, init=False)

    def __repr__(self):
        return f"{self.state.title()} {self.file_type.title()} Folder"

    @property
    def logger(self):
        # return Logger(module_name="FolderReader")
        return None

    @property
    def files(self) -> List[Path]:
        if self._files_need_update:
            self._compute_files()
        return self._files

    @files.setter
    def files(self, value: List[Path]):
        self._files = value
        self._files_need_update = False
        self._newest_file_need_update = True  # Newest file might have changed

    def _compute_files(self):
        self._files = [
            Path(x) for x in self.folder_path.iterdir() if x.is_file() and (x.suffix == ".csv" or x.suffix == ".txt")
        ]
        # self.logger.info(f"Found {len(self._files)} files in {self.folder_path.stem}")
        self._files_need_update = False

    @property
    def newest_file(self) -> Path:
        if self._newest_file_need_update:
            self._compute_newest_file()
        return self._newest_file

    @newest_file.setter
    def newest_file(self, value: Path):
        self._newest_file = value
        self._newest_file_need_update = False

    def _compute_newest_file(self):
        self._newest_file = sorted(self.files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
        # self.logger.info(f"Newest file is {self._newest_file}")
        self._newest_file_need_update = False

    async def async_csv_files(self) -> List[Path]:
        _files = [
            Path(x) for x in self.folder_path.iterdir() if x.is_file() and x.suffix == ".csv"
        ]
        if len(_files) == 0:
            _files = [
                Path(x) for x in self.folder_path.iterdir() if x.is_file() and x.suffix == ".txt"
            ]
        # self.logger.info(f"Found {len(_files)} files in {self.folder_path.stem}")
        self._files = _files
        return self._files

    async def async_newest_file(self):
        self.newest_file = sorted(
            await self.async_csv_files(), key=lambda x: x.stat().st_mtime, reverse=True
        )[0]
        # self.logger.info(f"Newest file is {self._newest_file.stem}")
        return self.newest_file

    def read(self):
        if not self._files or not self._newest_file:
            self.files = asyncio.run(self.async_csv_files())
            self.newest_file = asyncio.run(self.async_newest_file())
        return self
