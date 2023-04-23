#!/usr/bin/env python
from app.loaders.tec_loader import TECFolderLoader
from app.funcs.general_funcs import write_pandas_schema
from app.search_tools.tec_search import ContributionSearch, ExpenseSearch, ResultCounter, TECSearchPrompt
import pandera as pa
import pandas as pd

# files = TECFolderLoader()
# cont = files.contributions.load_records()
# write_pandas_schema(pd.DataFrame(cont), 'tec_contribution_schema')
# expenses = files.expenses.validate_category(load_to_sql=True)
# contributions = files.contributions.validate_category(load_to_sql=True)

berry = ExpenseSearch('BERRY COMMUNICATIONS')

df = berry.to_df()

counts = ResultCounter(berry)

berry_year = counts.by_year(include_total=False)

macias = ExpenseSearch('MACIAS STRATEGIES')
macias_df = macias.to_df()
macias_counts = ResultCounter(macias)
macias_year = macias_counts.by_year(include_total=False)


axiom = ExpenseSearch('AXIOM STRATEGIES')
axiom_df = axiom.to_df()
axiom_counts = ResultCounter(axiom)
axiom_year = axiom_counts.by_year()

# Make sure all collumn names are strings and sort alphabetically
# merged.columns = sorted([str(col) for col in merged.columns])
#
# current_clients = berry_year[berry_year[2022] != "$0.00"]
#
# list(current_clients.index)