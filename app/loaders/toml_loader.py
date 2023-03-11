from pathlib import Path
import tomli
from dataclasses import dataclass, field
from typing import Generator
from app.funcs.category_funcs import category_iterator


@dataclass
class TomlLoader:
    state: str
    config: dict = field(init=False)
    field_categories: Generator = field(init=False)

    @property
    def path(self) -> Path:
        return Path(__file__).parent.parent / 'utils' / 'field_library' / f'{self.state.lower()}.toml'

    def load_config(self) -> dict:
        with open(self.path, 'rb') as f:
            self.config = tomli.load(f)
            return self.config

    def load_field_categories(self) -> Generator:
        self.field_categories = category_iterator(self.config)
        return self.field_categories

    def __post_init__(self):
        self.load_config()
        self.load_field_categories()


if __name__ != '__main__':
    texas = TomlLoader('Texas')
