
# TOML File Reader
::: state_voterfiles.utils.readers.toml_reader
[//]: # (## TomlReader - Read TOML files into Python dictionaries)

[//]: # ()
[//]: # (`TomlReader` is a simple class that allows you to read TOML files and convert them into Python dictionaries. It uses the tomli package to parse the TOML file and return the resulting dictionary.)

[//]: # ()
[//]: # (### Installation)

[//]: # (Before using `TomlReader`, you will need to install the tomli package. You can do this using pip:)

[//]: # (```)

[//]: # (pip install tomli)

[//]: # (```)

[//]: # ()
[//]: # (Once you have installed tomli, you can install `TomlReader` by copying the code into a Python file and importing it.)

[//]: # ()
[//]: # (### Usage)

[//]: # (To use `TomlReader`, you will first need to create an instance of the class by providing it with the path to the TOML file you wish to read. Once you have created an instance, you can access the data in the TOML file using the data property.)

[//]: # ()
[//]: # (Here is an example:)

[//]: # ()
[//]: # (``` py title="toml_reader.py")

[//]: # (from dataclasses import dataclass, field)

[//]: # (from pathlib import Path)

[//]: # (import tomli)

[//]: # (    )
[//]: # (@dataclass)

[//]: # (class TomlReader:)

[//]: # (    _file: Path)

[//]: # (    _data: dict = field&#40;init=False&#41;)

[//]: # ()
[//]: # ()
[//]: # (    @property)

[//]: # (    def data&#40;self&#41;:)

[//]: # (        with open&#40;self._file, 'rb'&#41; as f:)

[//]: # (            return tomli.load&#40;f&#41;)

[//]: # ()
[//]: # (# Create an instance of TomlReader with the path to the TOML file)

[//]: # (reader = TomlReader&#40;Path&#40;'/path/to/myfile.toml'&#41;&#41;)

[//]: # ()
[//]: # (# Access the data in the TOML file using the data property)

[//]: # (mydata = reader.data)

[//]: # ()
[//]: # (# Now you can use the data in your Python code)

[//]: # (print&#40;mydata['some_key']&#41;)

[//]: # (```)

[//]: # ()
[//]: # (In the example above, mydata will be a Python dictionary containing the data in the TOML file.)

[//]: # ()
[//]: # (### Conclusion)

[//]: # (`TomlReader` is a simple class that allows you to read TOML files and convert them into Python dictionaries. It is easy to use and can be a useful tool when working with TOML files in Python.)