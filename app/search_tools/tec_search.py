from dataclasses import dataclass, field
from app.conf.tec_postgres import sessionmaker, SessionLocal
from app.getters.tec_contribution_getter import TECRecordGetter
from app.conf.config import CampaignFinanceConfig
from typing import List, Protocol, ClassVar, Type
from collections import namedtuple
import pandas as pd


@dataclass
class ResultOptions:
    """
    Represents the result options of a database query.

    Attributes:
        result (List): A list of dictionaries representing the query results.

    Methods:
        __iter__(): Returns an iterator for the query results.
        _dtypes() -> dict: Returns a dictionary of the column names and their data types.
        pandas_types(): Replaces None, date, and UUID with their pandas equivalents.
        to_df() -> pandas.DataFrame: Returns a pandas DataFrame of the query results.
    """
    result: List

    def __iter__(self):
        return iter(self.result)

    @property
    def _dtypes(self) -> dict:
        """
        Returns a dictionary of the column names and their data types.
        """
        return {k: v.__class__.__name__ for r in self.result for k, v in r.items()}

    @property
    def pandas_types(self):
        """
        Replaces None, date, and UUID with their pandas equivalents.
        """
        dtypes = self._dtypes
        # Replace values == 'date' with pd.Datetime in dtypes
        for k, v in dtypes.items():
            if v in ['date', 'datetime']:
                dtypes[k] = 'datetime64[ns]'
            if v == 'NoneType':
                dtypes[k] = 'object'
            if v == 'UUID':
                dtypes[k] = 'object'
        return dtypes

    def to_df(self):
        """
        Returns a pandas DataFrame of the query results.
        """
        return pd.DataFrame(self.result).astype(self.pandas_types)


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
    result: ResultOptions = field(init=False)
    record_type: str
    __connection: ClassVar[SessionLocal]
    __sql_table: ClassVar[CampaignFinanceConfig.SQL_MODEL]
    _getter: ClassVar[TECRecordGetter]
    organization: bool

    @property
    def query(self):
        return self._query.upper()

    def fetch(self, query=None, record_type=None) -> None:
        ...

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
    result: ResultOptions = field(init=False)
    record_type: str = CampaignFinanceConfig.RECORD_EXPENSE_TYPE
    __connection: ClassVar[SessionLocal] = SessionLocal
    __sql_table: ClassVar[Type[CampaignFinanceConfig.SQL_MODEL]] = CampaignFinanceConfig.SQL_MODEL
    _getter: ClassVar[TECRecordGetter] = TECRecordGetter
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

            self.result = ResultOptions(_result)
        return self

    def __post_init__(self):
        self.fetch()


@dataclass
class ContributionSearch(QueryResults):
    _query: str
    result: ResultOptions = field(init=False)
    record_type: str = CampaignFinanceConfig.RECORD_CONTRIBUTION_TYPE
    __connection: ClassVar[SessionLocal] = SessionLocal
    __sql_table: ClassVar[Type[CampaignFinanceConfig.SQL_MODEL]] = CampaignFinanceConfig.SQL_MODEL
    _getter: ClassVar[TECRecordGetter] = TECRecordGetter
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
            self.result = ResultOptions(_result)
        return self

    def __post_init__(self):
        self.fetch()


# TODO: Fix counter to work with both ContributionSearch and ExpenseSearch add as a Var in QueryResults
@dataclass
class ResultCounter:
    _data: ContributionSearch or ExpenseSearch
    field: str = 'filerNameFormatted'

    @property
    def data(self):
        return self._data.to_df()

    def by_year(self, df: pd.DataFrame = None) -> pd.DataFrame:
        if not df:
            pass
        else:
            if not isinstance(df, pd.DataFrame):
                raise TypeError('df must be a pandas DataFrame')

        df = self.data

        _year, _money_field, _entity_column = (
            CampaignFinanceConfig.CONTRIBUTION_DATE_COLUMN,
            CampaignFinanceConfig.CONTRIBUTION_AMOUNT_COLUMN,
            'filerNameFormatted'
        ) if self.data.__class__.__name__ == 'ContributionSearch' else (
            CampaignFinanceConfig.EXPENDITURE_DATE_COLUMN,
            CampaignFinanceConfig.EXPENDITURE_AMOUNT_COLUMN,
            'payeeNameOrganization'
        )
        _crosstab = pd.crosstab(
            columns=df[_year].dt.year,
            index=df[_entity_column].sort_values(ascending=True),
            values=df[_money_field],
            aggfunc='sum',
            margins=True,
            margins_name='Total')
        result = _crosstab.dropna(how='all', axis=0).fillna(0).applymap('${:,.2f}'.format)
        return result
