# Search Methods
This module provides two data classes, `ExpenseSearch` and `ContributionSearch`, which allow you to search through expenses and contributions respectively, using a SQL query. The search queries can be executed in a PostgreSQL database through SQLAlchemy ORM.

## Example
```py title="main.py"
from app.search_tools.tec_search import ExpenseSearch, ContributionSearch
berry = ExpenseSearch('BERRY COMMUNICATIONS')
```

## Classes

### QueryResults
This class is a protocol for all query result classes. It defines the following attributes:

#### Attributes

* `_query`: The query to execute.
* `result`: The result options of the query.
* `record_type`: The type of record being queried.
* `_pandas_schema`: A class variable containing the Pandas schema for the query results.
* `__connection`: A class variable containing the SQLAlchemy database session.
* `__sql_table`: A class variable containing the SQLAlchemy model to query.
* `_getter`: A class variable containing the getter class for transforming SQLAlchemy models into Pydantic models.
* `organization`: True if searching for an organization, False otherwise.


#### Methods

* `query() -> str`: Returns the query to execute.
* `fetch(query: str = None, record_type: str = None) -> None`: Executes the query and stores the results.
* `to_df() -> pd.DataFrame`: Returns a Pandas DataFrame of the query results.
* `__post_init__() -> None`: Executes the fetch method after class initialization.

### `ExpenseSearch` & `ContributionSearch`
These classes contain the needed requirements for each type of search. Both inherit from QueryResults protocol.

