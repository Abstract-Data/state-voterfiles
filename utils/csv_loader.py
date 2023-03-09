import csv
from pathlib import Path
import re
from dataclasses import dataclass, field


@dataclass
class VoterFileLoader:
    def __init__(self, file: Path):
        self._file = file
        self._data = field(init=False)

    @property
    def data(self):
        if self._file.suffix == '.txt':
            _delim = ','
        else:
            _delim = None
        with open(self._file, 'r') as f:
            self._data = {k: v for k, v in enumerate(csv.DictReader(f, delimiter=_delim))}
        return self._data

    @data.setter
    def data(self, data: dict):
        self._data = data

    @staticmethod
    def format_keys(record_dict: dict) -> dict:
        _updated_data = {}
        for index, record in record_dict.items():
            updated_record = {}
            for k, v in record.items():
                _reformat_key = re.sub(r'(/)', '-', k)
                if _reformat_key is not None:
                    updated_record[_reformat_key] = v
                else:
                    updated_record[k] = v
            _updated_data[index] = updated_record
        return _updated_data

