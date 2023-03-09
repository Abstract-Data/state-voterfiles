from pathlib import Path
import tomli
from dataclasses import dataclass, field

@dataclass
class TomlReader:
    _file: Path
    _data: dict = field(init=False)


    @property
    def data(self):
        with open(self._file, 'rb') as f:
            return tomli.load(f)
