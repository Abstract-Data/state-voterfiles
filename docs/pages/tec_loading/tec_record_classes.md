## TECRecord
The `TECRecord `class represents a record from a TEC file. It contains the data from the record, the record's category, and the appropriate validator and SQL model based on the record's category.

###  Attributes
* `data`: A dictionary of the record's data.
* `category`: The record's category.
* `validator`: The appropriate validator based on the record's category.
* `sql_model`: The appropriate SQL model based on the record's category.

### Methods
* `get_validator()`: Checks the record's category and returns the appropriate validator and SQL model.

<br>

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

<br>

## TECCategory
The `TECCategory` class represents a category of records in a TEC dataset. It provides a number of methods for working with TEC records, including loading records from files, validating records, and loading records to a SQL database.

### Attributes
* `category`: A generator of Path objects representing the files in the category.
* `category_fields`: A dictionary of the category's fields.
* `passed`: A dictionary of records that passed validation.
* `failed`: A dictionary of records that failed validation.
* `records`: A list of records from the category.
* `sql_models`: A list of SQL models from the category.

### Properties
* `files`: A generator of `TECFile` objects.

### Methods
* `read_files(cls, cat) -> Generator[TECFile, None, None]` <br>
  This class method returns a generator of TECFile objects for the files in the category.


* `get_category_keys(self) -> dict` <br>
  This method returns a dictionary of the category's fields.


* `load_files(self)` <br>
  This method loads the records from the category's files and returns a dictionary of TECFile objects.


* `load_records(self, passed_only=True)` <br>
  This method loads the records from the category's files and returns a list of records.


* `validate_category(self, load_to_sql: bool = False) -> object` <br>
  This method validates the records in the category and returns a dictionary of passed and failed records.


* `load_file_to_sql(cls, models: Generator, session: sessionmaker = SessionLocal)` <br>
  This class method loads the records in the category to a SQL database.