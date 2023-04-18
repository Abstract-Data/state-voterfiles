---
title: State Voter File Reader & Validator
---

# Abstract Data <br> State Voter File Reader & Validator

## Features

* `class TomlReader` - Read state column fields into Python
* `class VoterInfo` - Map column fields to class for reference
* `class VoterFileLoader` - Load a state voter file

## Example

```py title="main.py"
from utils.toml_reader import TomlReader
from utils.csv_loader import VoterFileLoader

tx = VoterFileLoader(Path(__file__).parent / 'voter_files' / 'texasnovember2022.csv')

tx_validator = StateValidator(
    file=tx,
    validator=TexasValidator,
    sql_model=TexasRecord,
    load_to_sql=True)

tx_validator.validate()
```

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
