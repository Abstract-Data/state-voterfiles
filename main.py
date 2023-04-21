from utils.toml_reader import TomlReader
from utils.csv_loader import VoterFileLoader
from funcs.column_formats import VoterInfo
from pathlib import Path
from pydantic import create_model, validator, ValidationError, root_validator
from typing import Optional
from datetime import date
from collections import Counter
from pprint import pp
import pandas as pd
from validatiors.texas import TexasValidator
from models.texas import TexasRecord
from tqdm import tqdm
import sys
from collections import Counter
import json
from utils.state_validator import StateValidator
from conf.postgres import Base, engine, SessionLocal
# from validatiors.validator_template import ValidatorTemplate


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
# db.rollback()

def ohio_file():
    ohio_cols = TomlReader('Ohio', Path.cwd() / 'state_fields' / 'ohio-fields.toml').data
    ohio_vf = VoterFileLoader(Path.cwd() / 'voter_files/202303 - HANCOCK OH VOTER REG.txt')
    return ohio_vf, ohio_cols


vf, cols = ohio_file()

ohio = TomlReader('Ohio', Path.cwd() / 'state_fields' / 'ohio-fields.toml')

# data = [r for r in vf.data]

# tx = VoterFileLoader(Path(__file__).parent / 'voter_files' / 'texasnovember2022.csv')
#
# tx_validator = StateValidator(
#     file=tx,
#     validator=TexasValidator,
#     sql_model=TexasRecord)
#
# tx_validator.validate()
# tx_validator.load_file_to_sql(tx_validator.passed)

# valid, invalid = [], []
#
# for record in tqdm(tx.data, desc='Validating Texas Records', position=0, unit='records'):
#     try:
#         _record = TexasValidator(**record)
#         valid.append(_record.dict())
#     except ValidationError as e:
#         invalid.append({'error': e,
#                         'record': record})
#     sys.stdout.write(f"\rValid: {len(valid):,} Invalid: {len(invalid):,}")
#     sys.stdout.flush()
#
# errors = pd.DataFrame(invalid)
# df = pd.DataFrame(valid)
# df.to_csv(Path.home() / 'Downloads' / '20230404_texas_valid.csv', index=False)

# df_raw = pd.DataFrame(tx.data)
#
# df_raw.notna().sum()
#
# df_raw['DOB'] = pd.to_datetime(df_raw['DOB'], errors='coerce')
# df_raw['DOB'].dt.year.value_counts().sort_index()
#
# zip_count = Counter(df_raw['RZIP'])
#
# year_crosstab = pd.crosstab(
#     index=df_raw['DOB'].dt.year.astype(int),
#     columns='count',
# )