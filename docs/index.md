---
title: State Voter File Reader & Validator
---

# Abstract Data <br> State Voter File Reader & Validator

## Features

* `class TomlReader` - Read state column fields into Python
* `class VoterInfo` - Map column fields to class for reference
* `class VoterFileLoader` - Load a state voter file

## Example

[//]: # (```py title="main.py")

[//]: # (from state_voterfiles.utils.readers import TomlReader)

[//]: # (from state_voterfiles.utils.loaders.state_loader import StateVoterFile)

[//]: # ()
[//]: # (tx = StateVoterFile&#40;Path&#40;__file__&#41;.parent / 'voter_files' / 'texasnovember2022.csv'&#41;)

[//]: # ()
[//]: # (tx_validator = StateValidator&#40;)

[//]: # (    file=tx,)

[//]: # (    validator=TexasValidator,)

[//]: # (    sql_model=TexasRecord,)

[//]: # (    load_to_sql=True&#41;)

[//]: # ()
[//]: # (tx_validator.validate&#40;&#41;)

[//]: # (```)

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
