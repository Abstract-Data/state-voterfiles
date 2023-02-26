from dataclasses import dataclass, field
from app.conf.tec_postgres import sessionmaker, SessionLocal
from app.getters.tec_contribution_getter import TECRecordGetter
from app.loaders.tec_expenses import CampaignFinanceConfig
from typing import List
from collections import namedtuple
import pandas as pd


PersonDetails = namedtuple('PersonDetails', ['first_name', 'last_name'])

@dataclass
class ResultOptions:
    result: List
    _result: List = field(init=False)

    def __iter__(self):
        return iter(self.result)

    @property
    def _dtypes(self) -> dict:
        return {k: v.__class__.__name__ for r in self.result for k, v in r.items()}

    @property
    def pandas_types(self):
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
        return pd.DataFrame(self.result).astype(self.pandas_types)



@dataclass
class ExpenseSearch:
    _query: str
    record_type: str = 'EXPN'
    __connection: sessionmaker = SessionLocal
    __sql_table: CampaignFinanceConfig.SQL_MODEL = CampaignFinanceConfig.SQL_MODEL
    _getter: TECRecordGetter = TECRecordGetter

    def __repr__(self):
        match self.record_type.upper():
            case 'RCPT' | 'CONTRIBUTION':
                return f'{self._query.title()} Contribution Search'
            case 'EXPN' | 'EXPENSE':
                return f'{self._query.title()} Expense Search'

    @property
    def query(self):
        return self._query.upper()

    @property
    def result(self):
        return self._result.result

    def to_df(self):
        return self._result.to_df()

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
                ExpenseSearch.__sql_table.payeeCompanyName.like(f'%{self.query}%'),
                ExpenseSearch.__sql_table.recordType == self.record_type)
            _result = [ExpenseSearch._getter.from_orm(x).dict() for x in response.all()]
        return ResultOptions(_result)

    def __post_init__(self):
        self._result = self.fetch()


@dataclass
class ContributionSearch:
    _query: str or PersonDetails
    organization: str = False
    _result: ResultOptions = field(init=False)
    record_type: str = 'RCPT'
    __connection: sessionmaker = SessionLocal
    __sql_table: CampaignFinanceConfig.SQL_MODEL = CampaignFinanceConfig.SQL_MODEL
    _getter: TECRecordGetter = TECRecordGetter

    def __repr__(self):
        match self.record_type.upper():
            case 'RCPT' | 'CONTRIBUTION':
                return f'{self._query.title()} Contribution Search'
            case 'EXPN' | 'EXPENSE':
                return f'{self._query.title()} Expense Search'

    @property
    def query(self):
        if self.organization:
            return self._query.upper()
        else:
            return PersonDetails(*self._query.upper().split(' '))

    @property
    def result(self):
        return self._result.result

    def to_df(self):
        return self._result.to_df()

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
                    ContributionSearch.__sql_table.contributorNameFirst.like(f'%{self.query.first_name}%'),
                    ContributionSearch.__sql_table.contributorNameLast.like(f'%{self.query.last_name}%'),
                    ContributionSearch.__sql_table.recordType == self.record_type)
            _result = [ContributionSearch._getter.from_orm(x).dict() for x in response.all()]
            self._result = ResultOptions(_result)
        return self

    def __post_init__(self):
        self.fetch()

