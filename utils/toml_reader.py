from pathlib import Path
import tomli
from typing import Protocol, Dict, ClassVar, Optional
from dataclasses import dataclass, field
from abc import abstractmethod, ABC, abstractproperty


def load_data(path: Path) -> dict:
    with open(path, 'rb') as f:
        return tomli.load(f)


@dataclass
class TomlReader:
    state: str
    file: Path

    def __str__(self):
        return f'{self.state} Toml Reader'

    def __repr__(self):
        return f'{self.state} Toml Reader'

    def __post_init__(self):
        self.data: Dict = load_data(self.file)
