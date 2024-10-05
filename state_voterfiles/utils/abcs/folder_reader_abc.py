import abc
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
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
    files: List[Path] = field(default_factory=list, init=False)
    newest_file: Path = field(default_factory=Path)
    _files_need_update: bool = field(default=True, init=False)
    _newest_file_need_update: bool = field(default=True)

    def __repr__(self):
        return f"{self.state.title()} {self.file_type.title()} Folder"


    async def async_csv_files(self) -> List[Path]:
        _files = [
            Path(x) for x in self.folder_path.iterdir() if x.is_file() and x.suffix == ".csv"
        ]
        if len(_files) == 0:
            _files = [
                Path(x) for x in self.folder_path.iterdir() if x.is_file() and x.suffix == ".txt"
            ]
        # self.logger.info(f"Found {len(_files)} files in {self.folder_path.stem}")
        self.files = _files
        return self.files

    async def async_newest_file(self):
        self.newest_file = sorted(
            await self.async_csv_files(), key=lambda x: x.stat().st_mtime, reverse=True
        )[0]
        # self.logger.info(f"Newest file is {self._newest_file.stem}")
        return self.newest_file

    def read(self):
        if not self.files or not self.newest_file:
            self.files = asyncio.run(self.async_csv_files())
            self.newest_file = asyncio.run(self.async_newest_file())
        return self
