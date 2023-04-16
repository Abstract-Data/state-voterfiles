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