import csv
from pathlib import Path
import re
from dataclasses import dataclass, field
import tqdm
import pandas as pd

@dataclass
class VoterFileLoader:
    def __init__(self, file: Path, **kwargs):
        self._file = file
        self._data = field(init=False)

    @property
    def data(self):
        if self._file.suffix == '.txt':
            _delim = ','
        else:
            _delim = None

        def read_file():
            with open(self._file, 'r') as f:
                _reader = csv.DictReader(f, delimiter=_delim) if _delim else csv.DictReader(f)
                for record in _reader:
                    yield record

        self._data = read_file()
        return self._data

            # self._data = {
            #     k: v for k, v in enumerate(
            #         csv.DictReader(f, delimiter=_delim) if _delim else csv.DictReader(f)
            #     )
            # }
        # yield self._data

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
