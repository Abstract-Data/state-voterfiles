## TomlReader - Read TOML files into Python dictionaries

`TomlReader` is a simple class that allows you to read TOML files and convert them into Python dictionaries. It uses the tomli package to parse the TOML file and return the resulting dictionary.

### Installation
Before using `TomlReader`, you will need to install the tomli package. You can do this using pip:
```
pip install tomli
```

Once you have installed tomli, you can install `TomlReader` by copying the code into a Python file and importing it.

### Usage
To use `TomlReader`, you will first need to create an instance of the class by providing it with the path to the TOML file you wish to read. Once you have created an instance, you can access the data in the TOML file using the data property.

Here is an example:

``` py title="toml_reader.py"
from dataclasses import dataclass, field
from pathlib import Path
import tomli
    
@dataclass
class TomlReader:
    _file: Path
    _data: dict = field(init=False)


    @property
    def data(self):
        with open(self._file, 'rb') as f:
            return tomli.load(f)

# Create an instance of TomlReader with the path to the TOML file
reader = TomlReader(Path('/path/to/myfile.toml'))

# Access the data in the TOML file using the data property
mydata = reader.data

# Now you can use the data in your Python code
print(mydata['some_key'])
```

In the example above, mydata will be a Python dictionary containing the data in the TOML file.

### Conclusion
`TomlReader` is a simple class that allows you to read TOML files and convert them into Python dictionaries. It is easy to use and can be a useful tool when working with TOML files in Python.