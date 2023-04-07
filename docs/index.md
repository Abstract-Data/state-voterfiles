# Abstract Data <br> State Voter File Reader & Validator

## Features

* `class TomlReader` - Read state column fields into Python
* `class VoterInfo` - Map column fields to class for reference
* `class VoterFileLoader` - Load a state voter file

## Project layout

    main  ...
    funcs/
        column_formats.py # Where `VoterInfo` class object is nested
    utils/ 
        csv_loader.py # CSV file reader
        toml_reader.py # Toml file reader
    state_fields/
        ohio-fields.toml # Ohio voter file fields
        texas-fields.toml # Texas voter file fields
