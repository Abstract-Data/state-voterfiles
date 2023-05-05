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
import validatiors.validator_template as vt
from pydantic.json import pydantic_encoder
from funcs.scratch_8 import assign_fields
from models.texas_json import TexasJSON

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# db.rollback()

def ohio_file():
    ohio_cols = TomlReader(Path.cwd() / 'state_fields' / 'ohio-fields.toml').data
    ohio_vf = VoterFileLoader(Path.cwd() / 'voter_files/202303 - HANCOCK OH VOTER REG.txt')
    return ohio_vf, ohio_cols


# vf, cols = ohio_file()


texas = TomlReader(Path.cwd() / 'state_fields' / 'texas-fields.toml')

# tx = VoterFileLoader(Path(__file__).parent / 'voter_files' / 'texasnovember2022.csv')
#
# data = [x for x in tqdm(tx.data)]
#
# state = vt.state
# valid = []
# invalid = []
#
# test_data = data[0]
# test_model = vt.SOSInfo(**test_data)
# texas_validator = TexasValidator(**test_data)
# texas_validator_json = texas_validator.json(indent=4)
# # for record in data[:1000]:
#     try:
#         r = vt.RecordValidator(**record,
#                                sec_of_state=vt.SOSInfo(**record),
#                                voter_details=vt.PersonDetails(**record),
#                                address={'raddress': vt.RegisteredAddress(**record),
#                                         'raddress_parts': vt.RegisteredAddressParts(**record),
#                                         'maddress': vt.MailingAddress(**record)},
#                                # raddress=vt.RegisteredAddress(**record),
#                                # raddress_parts=vt.RegisteredAddressParts(**record),
#                                # maddress=vt.MailingAddress(**record),
#                                districts={
#                                    'precinct': vt.VotingPrecinct(**record),
#                                    'city': vt.CityDistricts(**record),
#                                    'courts': vt.CourtDistricts(**record),
#                                    'county': vt.CountyDistricts(**record),
#                                    'state': vt.StateDistricts(**record),
#                                    'federal': vt.FederalDistricts(**record),
#                                },
#
#                                # court_districts=vt.CourtDistricts(**record),
#                                # voting_precinct=vt.VotingPrecinct(**record),
#                                # city_districts=vt.CityDistricts(**record),
#                                # county_districts=vt.CountyDistricts(**record),
#                                # state_districts=vt.StateDistricts(**record),
#                                # federal_districts=vt.FederalDistricts(**record),
#                                )
#         valid.append(r)
#     except ValidationError as e:
#         invalid.append({'error': e,
#                         'record': record})
#
# session = SessionLocal()
# # Base.metadata.create_all(engine)
# # valid_json = [x.json() for x in valid]
# # valid_json_dict = [json.loads(x) for x in valid_json]
# # models = [TexasJSON(**x) for x in valid_json_dict]
# # session.add_all(models)
# # session.commit()
# #
# # session.rollback()
# texas_return = iter(session.query(TexasJSON).all())
# for result in texas_return:
#     print(vt.RecordValidator.construct(**dict(result)))
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
