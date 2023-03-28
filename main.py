#!/usr/bin/env python

from app.search_tools.tec_search import ContributionSearch, ExpenseSearch, ResultCounter, TECSearchPrompt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

macias = TECSearchPrompt()

wilks = TECSearchPrompt()