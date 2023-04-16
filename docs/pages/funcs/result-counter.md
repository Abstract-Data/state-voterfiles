# Result Aggregations
The `ResultCounter` class is a data processing class that is designed to be used with data from either `ContributionSearch` or `ExpenseSearch` classes. It provides a method called by_year that takes in a pandas DataFrame as input, groups the data by year and filer name, and returns a crosstab of the data that shows the total amount for each filer name for each year. This class has been defined using Python 3's dataclass decorator.

## Example Usage
```py title="main.py"
from app.search_tools.tec_search import ContributionSearch, ExpenseSearch, ResultCounter,

berry = ExpenseSearch('BERRY COMMUNICATIONS')

df = berry.to_df()

counts = ResultCounter(berry)

berry_by_year = counts.by_year()
```

### Class Variables
The `ResultCounter` class has three private instance variables:

* `_data`: An instance of ContributionSearch or ExpenseSearch.
* `_amount_field`: A string that represents the name of the amount field in the data.
* `_date_field`: A string that represents the name of the date field in the data.
* `_filer_name_field`: A string that represents the name of the filer name field in the data.

### Class Methods
* `pandas_schema` <br> This is a property that returns a TECExpensePandasSchema instance if _data is an instance of ExpenseSearch. Otherwise, it returns None.


* `data` <br>
  This is a property that converts _data to a pandas DataFrame and returns it.


* `get_fields` <br>
  This method returns a tuple of three strings that represent the names of the amount field, date field, and filer name field in the data, depending on whether _data is an instance of ContributionSearch or ExpenseSearch.


* `by_year` <br>
  This method groups the data by year and filer name, and returns a crosstab of the data that shows the total amount for each filer name for each year. It takes in a pandas DataFrame as input, but if no DataFrame is provided, it uses the data property to retrieve the DataFrame. If the input is not a pandas DataFrame, a TypeError is raised.



* `post_init` <br>
  This is a special method that is called after the instance has been initialized. It sets the values of _amount_field, _date_field, and _filer_name_field by calling the get_fields method.