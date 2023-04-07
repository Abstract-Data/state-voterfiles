## VoterFileLoader - Load voter data from a file

VoterFileLoader is a class that allows you to load voter data from a file and convert it into a dictionary. It can handle both CSV and TXT file formats, and can also format the keys in the resulting dictionary to make them easier to work with.

### Installation
`VoterFileLoader` is not a separate package and is provided as a class within your own code.

### Usage
To use `VoterFileLoader`, you will first need to create an instance of the class by providing it with the path to the voter file you wish to load. Once you have created an instance, you can access the data in the voter file using the data property.

Here is an example:

``` py title="csv_loader.py"
from dataclasses import dataclass, field
from pathlib import Path
import csv
import re


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
```

In the example above, `VoterFileLoader` will load a voter file in either CSV or TXT format, depending on the file extension. The resulting data will be returned as a dictionary. You can also use the `format_keys` method to format the keys in the resulting dictionary.

To use `VoterFileLoader` in your own code, you can create an instance of the class and access the data using the data property:

``` py 
# Create an instance of VoterFileLoader with the path to the voter file
loader = VoterFileLoader(Path('/path/to/myfile.csv'))

# Access the data in the voter file using the data property
voter_data = loader.data

# Now you can use the voter data in your Python code
print(voter_data)
```


### Conclusion
`VoterFileLoader` is a simple class that allows you to load voter data from a file and convert it into a dictionary. It is easy to use and can be a useful tool when working with voter data in Python.