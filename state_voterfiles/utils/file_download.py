from dataclasses import dataclass, field
import requests
from zipfile import ZipFile
import sys
from tqdm import tqdm
from pathlib import Path
from datetime import date
from typing import ClassVar, Type
import os
import tomli

TEMP_FOLDER: Path = Path(__file__).parent.parent / 'tmp'
STATE_FIELDS_FOLDER: Path = Path(__file__).parent.parent / 'field_references' / 'states'
COUNTY_FIELDS_FOLDER: Path = Path(__file__).parent.parent / 'field_references' / 'counties'


@dataclass
class DownloadFile:
    """
    Download file from url and extract to temp folder
    :param state_or_county: str

    :return: object
    """
    state_or_county: str
    file_url: str = field(init=False)
    tmp: ClassVar[Path] = TEMP_FOLDER
    _state_county_folder: Path = field(init=False)
    _file_list: list = field(init=False)

    def __post_init__(self):
        self._new_file_name_prefix = f"{''.join(str(date.today()).split('-'))}_{self.state_or_county.lower()}"
        self.locate_state_or_county_fields()

    def locate_state_or_county_fields(self):
        file_list = [Path(x) for x in STATE_FIELDS_FOLDER.iterdir()]
        file_list.extend([Path(x) for x in COUNTY_FIELDS_FOLDER.iterdir()])
        for state in file_list:
            if self.state_or_county.lower() == state.stem.lower():
                self._state_county_folder = Path(state)

                # Get file url from toml file
                with open(self._state_county_folder, 'rb') as f:
                    _data = tomli.load(f)
                    self.file_url = _data.get('download_url')
            else:
                raise ValueError(f'Cannot find configs for {self.state_or_county.title()}')

            return self

    def download(self, read_from_temp: bool = True) -> Path or object:
        _zipfile = \
            f"{DownloadFile.tmp}/'{self._new_file_name_prefix}.zip"

        def download_file() -> None:
            # download files
            with requests.get(self.file_url, stream=True) as resp:
                # check header to get content length, in bytes
                total_length = int(resp.headers.get("Content-Length"))

                # Chunk download of zip file and write to temp folder
                with open(_zipfile, 'wb') as f:
                    for chunk in tqdm(resp.iter_content(
                            chunk_size=1024),
                            unit='KB',
                            desc='Downloading'):
                        if chunk:
                            f.write(chunk)
                return None

        def extract_zipfile() -> None:
            self._file_list = []
            # extract zip file to temp folder
            with ZipFile(_zipfile, 'r') as myzip:
                for extracted_file in enumerate(myzip.namelist(), 1):
                    _file = Path(myzip.extract(extracted_file[1]))  # extract file to tmp folder
                    _renamed_file = _file.rename(
                        f"{Path(DownloadFile.tmp)}/{self._new_file_name_prefix}_{extracted_file[0]}{_file.suffix}"
                    )  # rename file to include enumeration and file extension of extracted file
                    self._file_list.append(Path(_renamed_file))  # add file to list of files in tmp folder
                os.unlink(_zipfile)

        try:

            if read_from_temp is False:
                # check if tmp folder exists

                if DownloadFile.tmp.exists() is False:
                    DownloadFile.tmp.mkdir()

                if DownloadFile.tmp.is_dir():
                    ask_to_make_folder = input("Temp folder already exists. Overwrite? (y/n): ")
                    if ask_to_make_folder.lower() == 'y':
                        download_file()
                        extract_zipfile()
                    else:
                        as_to_change_folder = input("Use temp folder as source? (y/n): ")
                        if as_to_change_folder.lower() == 'y':
                            if DownloadFile.tmp.glob('*.csv') == 0 and DownloadFile.tmp.glob('*.zip') == 1:
                                extract_zipfile()
                                return self
                        else:
                            sys.exit()  # set folder to temp folder

        # remove tmp folder if user cancels download
        except KeyboardInterrupt:
            for file in DownloadFile.tmp.iterdir():
                file.unlink()
            DownloadFile.tmp.rmdir()
            print('Temp Folder Removed')

            return self
