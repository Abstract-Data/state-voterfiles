from pathlib import Path
import tomli
from typing import Dict
from dataclasses import dataclass, field

@dataclass
class TomlReader:
    _file: Path
    data: Dict = field(init=False)

    def load_data(self) -> Dict:
        with open(self._file, 'rb') as f:
            return tomli.load(f)

    def __post_init__(self):
        self.data = self.load_data()

