from utils.toml_reader import TomlReader
from utils.csv_loader import VoterFileLoader
from funcs.column_formats import ohio
from pathlib import Path
from pydantic import create_model, validator, ValidationError, root_validator
from typing import Optional
from datetime import date
from collections import Counter
from pprint import pp
import pandas as pd

ohio_cols = TomlReader(Path.cwd() / 'state_formatting' / 'ohio-voter-format.toml').data

ohio_vf = VoterFileLoader(Path.cwd() / 'voter_files/202303 - HANCOCK OH VOTER REG.txt')

example_record = ohio_vf.data[0]


def format_date(dt: str) -> date:
    if dt:
        _split = [int(x) for x in dt.split('-')]
        return date(*_split)


def zip5_length(zip5: str) -> str:
    if zip5:
        if len(zip5) == 5:
            return zip5
        else:
            ValidationError('Invalid zip5', model=OhioModel)


def zip4_length(zip4: str) -> str:
    if zip4:
        if len(zip4) == 4:
            return zip4
        else:
            ValidationError('Invalid zip4', model=OhioModel)


def remove_blanks(cls, values) -> None:
    for k, v in values.items():
        if v == '':
            values[k] = None
    return values


def party_formatter(cls, values) -> str:
    for election in ohio.elections:
        voted = values.get(election.date)
        if voted:
            for code, party in ohio._party.items():
                if code == voted:
                    values[election.date] = party
    return values


def registered_party(party: str) -> str:
    if party:
        for code, _party in ohio._party.items():
            if code == party:
                return _party
        else:
            return party


def export_to_csv(data_file, name: str):
    data_file.to_csv(Path.home() / 'Downloads' / f'{date.today()}_{name}.csv')


def sum_columns(df):
    df.loc['total', :] = df.sum(axis=0, numeric_only=True)
    df['avg'] = df.mean(axis=1, numeric_only=True)
    # Set numeric columns to integers with thousands separator
    for col in df.columns:
        if df[col].dtype == 'float':
            df[col] = df[col].astype('int').map('{:,}'.format)
    return df


validators = {
    'registration_date':
        validator(ohio.voter_info.registration_date)(format_date),
    'dob':
        validator(ohio.voter_info.dob)(format_date),
    'zip5':
        validator(ohio.registration_address.zip5, ohio.mailing_address.zip5)(zip5_length),
    'zip4':
        validator(ohio.registration_address.zip4, ohio.mailing_address.zip4)(zip4_length),
    'root':
        root_validator()(remove_blanks),
    'elections_party_formatter':
        root_validator()(party_formatter),
    'registered_party':
        validator(ohio.voter_info.political_party)(registered_party)
}

OhioModel = create_model(
    'OhioModel',
    **{k: (type(v).__name__, Optional) for k, v in example_record.items()},
    __validators__=validators)


def generate_valid_records(data_file, model=OhioModel):
    for record in data_file.data.values():
        yield model(**record)


valid = generate_valid_records(ohio_vf)

records = [x.dict() for x in valid]

vf = pd.DataFrame(records).replace({None: pd.NA})
vf = vf.dropna(axis=1, how='all')

primaries = [x for x in vf.columns.to_list() if x.startswith('PRIMARY')][-10:]
general = [x for x in vf.columns.to_list() if x.startswith('GENERAL')][-10:]

no_ward = vf[vf[ohio.county.ward].notna()]
findlay_voters = no_ward[no_ward[ohio.county.ward].str.contains('FINDLAY')]


primary_counts = findlay_voters.groupby(ohio.county.ward)[primaries].count().reset_index()
general_counts = findlay_voters.groupby(ohio.county.ward)[general].count().reset_index()

# Drop Primary columns if sum is less than 10
primary_counts = primary_counts.drop([x for x in primaries if primary_counts[x].sum() < 50], axis=1)
general_counts = general_counts.drop([x for x in general if general_counts[x].sum() < 50], axis=1)

primary_counts = sum_columns(primary_counts)
general_counts = sum_columns(general_counts)

export_to_csv(primary_counts, 'findlay_primary_counts')
export_to_csv(general_counts, 'findlay_general_counts')