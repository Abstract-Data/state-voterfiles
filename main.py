#!/usr/bin/env python
from app.loaders.tec_loader import TECFolderLoader
from app.search_tools.tec_search import ContributionSearch, ExpenseSearch, ResultCounter, TECSearchPrompt

files = TECFolderLoader()
expenses = files.expenses.validate_category(load_to_sql=True)
contributions = files.contributions.validate_category(load_to_sql=True)
