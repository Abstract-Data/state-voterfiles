## TECFile
Represents a TEC (Texas Ethics Commission) file. Generates records from the file on instantiation.

### Attributes
* `file`: Path - The file path.
* `passed`: List - A list of records that passed validation.
* `failed`: List - A list of records that failed validation.
* `to_sql`: Generator[RECORD_SQL_MODEL, None, None] - A generator of records to be loaded into the database.
* `validator`: settings.VALIDATOR - The file's validator.
* `sql_model`: settings.SQL_MODEL - The file's SQL model.

### Properties
* `records`: Generator[TECRecord, None, None] - A generator of records from the file.

### Methods
* `load_records(passed_only=True) -> Dict[int, RECORD_SQL_MODEL]` - Returns a dictionary of records from the file.
* `validate_file() -> [List, List]` - Validates the file and returns a list of passed and failed records.
* `generate_models() -> Generator[RECORD_SQL_MODEL, None, None]` - Returns a generator of SQL models that passed validation.
