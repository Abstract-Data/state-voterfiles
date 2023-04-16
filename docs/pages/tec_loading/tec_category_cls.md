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