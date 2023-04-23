from dataclasses import dataclass, field
from app.conf.tec_postgres import sessionmaker, SessionLocal
from app.getters.tec_contribution_getter import TECContributionGetter
from app.getters.tec_expense_getter import TECExpenseGetter
from app.conf.config import CampaignFinanceConfig
from typing import List, Protocol, ClassVar, Type, Optional
import pandas as pd
from app.pandas_schemas.tec_expense_schema import TECExpensePandasSchema
import pandera as pa


@dataclass
class QueryResults(Protocol):
    """
    Protocol for all query results classes.

    Attributes:
        _query (str): The query to execute.
        result (ResultOptions): The result options of the query.
        record_type (str): The type of record being queried.
        __connection (Session): The SQLAlchemy database session.
        __sql_table (Type[CampaignFinanceConfig.SQL_MODEL]): The SQLAlchemy model to query.
        _getter (TECRecordGetter): The getter class for transforming SQLAlchemy models into Pydantic models.
        organization (bool): True if searching for an organization, False otherwise.

    Methods:
        query() -> str: Returns the query to execute.
        fetch(query: str = None, record_type: str = None) -> None: Executes the query and stores the results.
        __post_init__() -> None: Executes the fetch method after class initialization.
    """
    _query: str
    result: List = field(init=False)
    record_type: str
    _pandas_schema: ClassVar[pa.DataFrameSchema]
    __connection: ClassVar[SessionLocal]
    __sql_table: ClassVar[CampaignFinanceConfig.EXPENSE_SQL_MODEL or CampaignFinanceConfig.CONTRIBUTION_SQL_MODEL]
    _getter: ClassVar[TECContributionGetter or TECExpenseGetter]
    organization: bool

    @property
    def query(self):
        return self._query.upper()

    def fetch(self, query=None, record_type=None) -> None:
        ...

    def to_df(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame of the query results.
        """
        return pd.DataFrame(self.result)

    def __post_init__(self):
        ...


@dataclass
class ExpenseSearch(QueryResults):
    """
    Represents a query for expenses.

    Attributes:
        _query (str): The search query string.
        result (ResultOptions): The query result with a list of options and total count.
        record_type (str): The record type of the expense.
        __connection (ClassVar): The database session.
        __sql_table (ClassVar): The SQL model for expenses.
        _getter (ClassVar): The class for converting SQL model objects to dictionaries.
        organization (bool): Whether to search for an organization instead of an individual.
"""
    _query: str
    result: List = field(init=False)
    dataframe: pd.DataFrame = field(init=False)
    record_type: str = CampaignFinanceConfig.TYPE_EXPENSE
    _pandas_schema: ClassVar[pa.DataFrameSchema] = TECExpensePandasSchema
    __connection: ClassVar[SessionLocal] = SessionLocal
    __sql_table: ClassVar[Type[CampaignFinanceConfig.EXPENSE_SQL_MODEL]] = CampaignFinanceConfig.EXPENSE_SQL_MODEL
    _getter: ClassVar[TECExpenseGetter] = TECExpenseGetter
    organization: bool = False

    @property
    def query(self):
        return self._query.upper()

    def fetch(self, query=None, record_type=None):
        if query:
            self._query = query
        if record_type:
            self.record_type = record_type
        response: str

        with self.__connection() as db:
            response = db.query(
                ExpenseSearch.__sql_table
            ).filter(
                ExpenseSearch.__sql_table.payeeNameOrganization.like(f'%{self.query}%'),
                ExpenseSearch.__sql_table.recordType == self.record_type)
            _result = [ExpenseSearch._getter.from_orm(x).dict() for x in response.all()]

            self.result = _result
        return self

    @pa.check_output(_pandas_schema, lazy=True)
    def to_df(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame of the query results.
        """
        self.dataframe = pd.DataFrame(self.result)
        return self.dataframe

    def __post_init__(self):
        self.fetch()


@dataclass
class ContributionSearch(QueryResults):
    _query: str
    result: List = field(init=False)
    record_type: str = CampaignFinanceConfig.TYPE_CONTRIBUTION
    __connection: ClassVar[SessionLocal] = SessionLocal
    __sql_table: ClassVar[
        Type[CampaignFinanceConfig.CONTRIBUTION_SQL_MODEL]] = CampaignFinanceConfig.CONTRIBUTION_SQL_MODEL
    _getter: ClassVar[TECContributionGetter] = TECContributionGetter
    organization: bool = False

    @property
    def query(self):
        if self.organization:
            return self._query.upper()
        else:
            first, last = self._query.upper().split(' ')
            return first, last

    def fetch(self, query=None, record_type=None):
        if query:
            self._query = query
        if record_type:
            self.record_type = record_type

        with self.__connection() as db:
            table = db.query(
                ContributionSearch.__sql_table
            )
            if self.organization:
                response = table.filter(
                    ContributionSearch.__sql_table.contributorNameOrganization.like(f'%{self.query}%'),
                    ContributionSearch.__sql_table.recordType == self.record_type)
            else:
                response = table.filter(
                    ContributionSearch.__sql_table.contributorNameFirst.like(f'%{self.query[0]}%'),
                    ContributionSearch.__sql_table.contributorNameLast.like(f'%{self.query[1]}%'),
                    ContributionSearch.__sql_table.recordType == self.record_type)
            _result = [ContributionSearch._getter.from_orm(x).dict() for x in response.all()]
            self.result = _result
        return self

    def __post_init__(self):
        self.fetch()


# TODO: Fix counter to work with both ContributionSearch and ExpenseSearch add as a Var in QueryResults
@dataclass
class ResultCounter:
    _data: ContributionSearch or ExpenseSearch
    _amount_field: str = field(init=False)
    _date_field: str = field(init=False)
    _filer_name_field: str = field(init=False)
    _vendor_donor_name: str = field(init=False)

    @property
    def pandas_schema(self):
        if isinstance(self._data, ExpenseSearch):
            return TECExpensePandasSchema

    @property
    def data(self):
        df = self._data.to_df()
        return df

    def get_fields(self):
        if self._data.__class__.__name__ == 'ContributionSearch':
            return CampaignFinanceConfig.CONTRIBUTION_AMOUNT_COLUMN, \
                CampaignFinanceConfig.CONTRIBUTION_DATE_COLUMN, \
                CampaignFinanceConfig.FILER_NAME_COLUMN, \
                CampaignFinanceConfig.CONTRIBUTOR_NAME_COLUMN
        else:
            return CampaignFinanceConfig.EXPENDITURE_AMOUNT_COLUMN, \
                CampaignFinanceConfig.EXPENDITURE_DATE_COLUMN, \
                CampaignFinanceConfig.FILER_NAME_COLUMN, \
                CampaignFinanceConfig.VENDOR_NAME_COLUMN

    def by_year(self, df: pd.DataFrame = None, include_origin=False, include_total=True) -> pd.DataFrame:
        if not df:
            pass
        else:
            if not isinstance(df, pd.DataFrame):
                raise TypeError('df must be a pandas DataFrame')

        df = self.data

        _crosstab = pd.crosstab(
            columns=df[self._date_field].dt.year,
            index=[
                df[self._filer_name_field],
                df[self._vendor_donor_name]
            ] if include_origin else df[self._filer_name_field],
            values=df[self._amount_field],
            aggfunc='sum',
            margins=include_total,
            margins_name='Total' if include_total else None)
        result = _crosstab.dropna(how='all', axis=0).fillna(0).applymap('${:,.2f}'.format)
        return result

    def __post_init__(self):
        self._amount_field, self._date_field, self._filer_name_field, self._vendor_donor_name = self.get_fields()


@dataclass
class TECSearchPrompt:
    _type_of_search_prompt: Optional[str] = field(init=False)
    result: ResultCounter = field(init=False)
    by_year: pd.DataFrame = field(init=False)
    _search_object: ContributionSearch or ExpenseSearch = field(init=False)
    _counter: ResultCounter = field(init=False)

    def ask_search_type(self):
        _type_of_search_prompt = input('Would you like to search for a contribution or an expense?')
        if _type_of_search_prompt.lower() == 'contribution':
            self._search_object = ContributionSearch(input('What is the name of the contributor?'))
        elif _type_of_search_prompt.lower() == 'expense':
            self._search_object = ExpenseSearch(input('What is the name of the payee?'))
        else:
            raise ValueError('Please enter either "contribution" or "expense"')
        self._type_of_search_prompt = _type_of_search_prompt
        return self._search_object

    def ask_search_query(self, result_object=None):
        return ResultCounter(result_object)

    def ask_by_year(self):
        want_by_year = input('Would you like to see the results by year? y/n')
        if want_by_year.lower() == 'y':
            _result = self.result.by_year()
            print(_result.to_markdown())
            return _result
        else:
            pass

    def __post_init__(self):
        self.ask_search_type()
        self.result = self.ask_search_query(self._search_object)
        self.by_year = self.ask_by_year()
