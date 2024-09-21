from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Generator


@dataclass
class TXTReader:

    def __init__(self, file: Path, **kwargs):
        self._file = file if isinstance(file, Path) else Path(file)
        self.records = None
        self.encoding = kwargs.get("encoding", "utf-8-sig")

    def read(self):
        def _read():
            with open(self._file, 'r') as f:
                records = f.readlines()
            data = []
            for record in records:
                _split = record.split("\t")
                row = []
                for item in _split:
                    if item == '""':
                        row.append(None)
                    else:
                        row.append(item)
                data.append(row)
            data = [item.replace('"', "") if isinstance(item, str) else item for item in data]
            yield data
        self.records = _read()
        return self.records

    def load(self):
        if not self.records:
            self.read()
        return [x for x in self.records]
