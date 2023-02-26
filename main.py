import pandas as pd

from app.search_tools.tec_search import ContributionSearch, ExpenseSearch

macias = ExpenseSearch('Macias Strategies')

wilks = ContributionSearch('Farris Wilks')

berry = ExpenseSearch('Berry Communications')


wilks_df = wilks.to_df()


def year_crosstab(entity):
    _crosstab = pd.crosstab(
        columns=wilks_df['contributionDt'].dt.year,
        index=[wilks_df[entity]],
        values=wilks_df['contributionAmount'],
        aggfunc='sum',
        margins=True,
        margins_name='Total')
    result = _crosstab.dropna(how='all', axis=0).fillna(0).applymap('${:,.2f}'.format)
    return result


type_columns = iter(['filerNameFormatted', 'filerCompanyNameFormatted'])
candidate = year_crosstab(next(type_columns))
pacs = year_crosstab(next(type_columns))
