from state_tools import SetupState, StateVoterFile


texas = SetupState('texas')

tx = StateVoterFile('texas')
pa = StateVoterFile('pennsylvania')
mt = StateVoterFile('montana')


def test_validation(state: StateVoterFile):
    state.read()
    state.validate()

    test_list = []
    counter = 0
    for r in state.validation.valid:
        counter += 1
        test_list.append(r)
        if counter > 100:
            break
    return test_list


tx_test = test_validation(tx)
pa_test = test_validation(pa)
mt_test = test_validation(mt)




# from state_voterfiles.utils.toml_reader import TomlReader
# from state_voterfiles.utils.csv_loader import CSVLoader
# from state_voterfiles.validatiors.texas import TexasValidator
# from tqdm import tqdm
# import state_voterfiles.validatiors.validator_template as vt
# from state_voterfiles.models.texas_json import TexasJSON
# from pathlib import Path
# import pandas as pd
# from state_voterfiles.conf.postgres import SessionLocal, Base, engine
# import json
# from state_voterfiles.funcs.json_funcs import flatten_json
# from state_voterfiles.funcs.validation import ValidateFile
#
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
#
#
# # db.rollback()
#
# def ohio_file():
#     ohio_cols = TomlReader(Path.cwd() / 'field_references' / 'ohio-fields.toml').data
#     ohio_vf = CSVLoader(Path.cwd() / 'voter_files/202303 - HANCOCK OH VOTER REG.txt')
#     return ohio_vf, ohio_cols
#
#
# # vf, cols = ohio_file()
#
# tx = CSVLoader(Path(__file__).parent / 'state_voterfiles' / 'voter_files' / 'texasnovember2022.csv')
#
# data = tx.load()
#
# texas_test_file = ValidateFile(data[:1000])
# texas_test_file.validate()

# for record in data[:1000]:
#     try:
#         r = vt.RecordValidator(**record,
#                                sec_of_state=vt.SOSInfo(**record),
#                                voter_details=vt.PersonDetails(**record),
#                                address=vt.AllAddresses(
#                                    raddress=vt.RegisteredAddress(**record),
#                                    raddress_parts=vt.RegisteredAddressParts(**record),
#                                    maddress=vt.MailingAddress(**record),
#                                ),
#                                # raddress=vt.RegisteredAddress(**record),
#                                # raddress_parts=vt.RegisteredAddressParts(**record),
#                                # maddress=vt.MailingAddress(**record),
#                                districts=vt.AllDistricts(
#                                    precinct=vt.VotingPrecinct(**record),
#                                    city=vt.CityDistricts(**record),
#                                    court=vt.CourtDistricts(**record),
#                                    county=vt.CountyDistricts(**record),
#                                    state=vt.StateDistricts(**record),
#                                    federal=vt.FederalDistricts(**record))
#                                )
#         valid.append(r)
#     except vt.ValidationError as e:
#         invalid.append({'error': e,
#                         'record': record})
#
# session = SessionLocal()
# Base.metadata.create_all(engine)

# models = [TexasJSON(**x) for x in valid_json_dict]
# session.add_all(models)
# session.commit()
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
