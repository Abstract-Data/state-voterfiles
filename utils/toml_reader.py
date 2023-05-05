from pathlib import Path
import tomli
from typing import Protocol, Dict, ClassVar, Optional, TypedDict
from dataclasses import dataclass, field
from abc import abstractmethod, ABC, abstractproperty

@dataclass
class TomlReader:
    _file: Path
    data: Dict = field(init=False)

    def load_data(self):
        with open(self._file, 'rb') as f:
            return tomli.load(f)

    def __post_init__(self):
        self.data = self.load_data()

