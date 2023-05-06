import uuid
from state_voterfiles.funcs.record_keygen import RecordKeyGenerator
from pydantic import ValidationError, validator, Field, root_validator, BaseModel, create_model
from typing import Optional, Dict
from datetime import date, datetime

from field_maps import texas

# TODO: Check to make sure the ElectionHistory validator is working as needed.

"""
==================
== FIELD DICTS ===
==================
"""

STATE = texas.data  # data from TOMLReader object

FIELD_FORMATS = STATE['FIELD-FORMATS']
VOTER_INFO = STATE['voter-registration']
VOTER_NAME = STATE['name']
VOTER_RADDRESS = STATE['address']['residence']
VOTER_RADDRESS_PARTS = STATE['address']['parts']['residence']
VOTER_MAILING_ADDRESS = STATE['address']['mail']
VOTING_DISTRICTS = STATE['VOTING-DISTRICTS']
ELECTION_DATES = STATE['ELECTION-DATES']
PARTY_AFFILIATIONS = STATE['PARTY-AFFILIATIONS']

"""
==================
== FUNCTIONS ===
==================
"""


def update_county_name(values: Dict):
    """
    If changes are needed to county name due to formatting issues.
    :param values:
    :return: values
    """
    if values['\ufeffCOUNTY']:
        values['COUNTY'] = values['\ufeffCOUNTY']
    return values


def clear_blank_strings(cls, values):
    """
    Clear out all blank strings or ones that contain 'null' from records.
    :param cls:
    :param values:
    :return:
    """
    for k, v in values.items():
        if v in ['', '"', 'null']:
            values[k] = None
    return values


def validate_dates(v):
    """
    Validator for dates, specifically for dob/edr. Takes `date_format` from TomlReader.data dictionary
    :param v:
    :return:
    """
    if v:
        try:
            return datetime.strptime(v, FIELD_FORMATS['date_format']).date()
        except ValueError or ValidationError:
            raise ValueError(f'Invalid date format: {v}')


def run_zip_validation(zip_code: str):
    """
    Validate zipcode based on structural patterns.
    :param zip_code:
    :return:
    """
    _length = len(str(zip_code))
    if _length == 5 and str(_length).isnumeric():
        zip5_col, zip4_col = zip_code, None
    elif _length == 9 and str(_length).isnumeric():
        zip5_col, zip4_col = zip_code[:5], zip_code[5:]
    elif _length == 10 and '-' in zip_code:
        zip5_col, zip4_col = zip_code.split('-')
    else:
        raise ValueError(f'Invalid zip code: {zip_code}')
    return zip5_col, zip4_col


"""
==================
== MODELS ===
==================
"""


class SOSInfo(BaseModel):
    vuid: str = Field(alias=VOTER_INFO['vuid'])
    edr: date = Field(alias=VOTER_INFO['registration_date'])
    status: Optional[str] = Field(alias=VOTER_INFO['registration_status'])
    political_party: Optional[str] = Field(alias=VOTER_INFO['political_party'])

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)
    _validate_edr = validator(VOTER_INFO['registration_date'],
                              pre=True,
                              allow_reuse=True,
                              check_fields=False)(validate_dates)


class PersonDetails(BaseModel):
    first_name: str = Field(alias=VOTER_NAME['last'])
    last_name: str = Field(alias=VOTER_NAME['first'])
    middle_name: Optional[str] = Field(alias=VOTER_NAME['middle'])
    suffix: Optional[str] = Field(alias=VOTER_NAME['suffix'])
    dob: date = Field(alias=VOTER_INFO['dob'])

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)
    _validate_dob = validator(VOTER_INFO['dob'],
                              pre=True,
                              allow_reuse=True,
                              check_fields=False)(validate_dates)


class RegisteredAddress(BaseModel):
    address1: Optional[str] = Field(alias=VOTER_RADDRESS['address1'])
    address2: Optional[str] = Field(alias=VOTER_RADDRESS['address2'])
    city: Optional[str] = Field(alias=VOTER_RADDRESS['city'])
    state: Optional[str] = Field(alias=VOTER_RADDRESS['state'])
    zip: Optional[int] = Field(alias=VOTER_RADDRESS['zip5'])
    zip4: Optional[int] = Field(alias=VOTER_RADDRESS['zip4'])
    country: Optional[str] = Field(alias=VOTER_RADDRESS['country'])
    postal_code: Optional[str] = Field(alias=VOTER_RADDRESS['postal_code'])

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    @root_validator(pre=True)
    @classmethod
    def validate_zip(cls, values):
        _registration_zip = values.get(VOTER_RADDRESS['zip5'], None)

        if _registration_zip:
            values['rzip'], values['rzip4'] = run_zip_validation(_registration_zip)

        return values

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)


class RegisteredAddressParts(BaseModel):
    house_number: Optional[str] = Field(alias=VOTER_RADDRESS_PARTS['house_number'])
    house_direction: Optional[str] = Field(
        alias=VOTER_RADDRESS_PARTS['house_direction'])
    street_name: Optional[str] = Field(alias=VOTER_RADDRESS_PARTS['street_name'])
    street_type: Optional[str] = Field(alias=VOTER_RADDRESS_PARTS['street_type'])
    street_suffix: Optional[str] = Field(
        alias=VOTER_RADDRESS_PARTS['street_suffix'])
    unit_number: Optional[str] = Field(alias=VOTER_RADDRESS_PARTS['unit_number'])
    unit_type: Optional[str] = Field(alias=VOTER_RADDRESS_PARTS['unit_type'])
    city: Optional[str] = Field(alias=VOTER_RADDRESS_PARTS['city'])
    state: Optional[str] = Field(alias=VOTER_RADDRESS_PARTS['state'])
    zip5: Optional[int] = Field(alias=VOTER_RADDRESS_PARTS['zip5'])
    zip4: Optional[int] = Field(alias=VOTER_RADDRESS_PARTS['zip4'])

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)

    @root_validator(pre=True)
    @classmethod
    def validate_zip(cls, values):
        _registration_zip = values.get(VOTER_RADDRESS_PARTS['zip5'], None)

        if _registration_zip:
            values['rzip5'], values['rzip4'] = run_zip_validation(_registration_zip)

        return values


class MailingAddress(BaseModel):
    address1: Optional[str] = Field(alias=VOTER_MAILING_ADDRESS['address1'])
    address2: Optional[str] = Field(alias=VOTER_MAILING_ADDRESS['address2'])
    city: Optional[str] = Field(alias=VOTER_MAILING_ADDRESS['city'])
    state: Optional[str] = Field(alias=VOTER_MAILING_ADDRESS['state'])
    zip5: Optional[int] = Field(alias=VOTER_MAILING_ADDRESS['zip5'])  # TODO: Fix TypeError for FieldInfo
    zip4: Optional[int] = Field(alias=VOTER_MAILING_ADDRESS['zip4'])  # TODO: Fix TypeError for FieldInfo

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)

    @root_validator(pre=True)
    @classmethod
    def validate_zip(cls, values):
        _mailing_zip = values.get(VOTER_MAILING_ADDRESS['zip5'])

        if _mailing_zip:
            values['mzip5'], values['mzip4'] = run_zip_validation(_mailing_zip)

        return values


class CourtDistricts(BaseModel):
    municipal: Optional[str] = Field(alias=VOTING_DISTRICTS['courts']['municipal'])
    county: Optional[str] = Field(alias=VOTING_DISTRICTS['courts']['county'])
    appeallate: Optional[str] = Field(alias=VOTING_DISTRICTS['courts']['appeallate'])

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)


class VotingPrecinct(BaseModel):
    name: Optional[str] = Field(alias=VOTING_DISTRICTS['precinct']['name'])
    number: Optional[str] = Field(alias=VOTING_DISTRICTS['precinct']['code'])

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)


class CityDistricts(BaseModel):
    name: Optional[str] = Field(alias=VOTING_DISTRICTS['city']['name'])
    school_district: Optional[str] = Field(alias=VOTING_DISTRICTS['city']['school_district'])

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)


class CountyDistricts(BaseModel):
    number: Optional[str] = Field(alias=VOTING_DISTRICTS['county']['number'])
    county_id: Optional[str] = Field(alias=VOTING_DISTRICTS['county']['id'])
    township: Optional[str] = Field(alias=VOTING_DISTRICTS['county']['township'])
    village: Optional[str] = Field(alias=VOTING_DISTRICTS['county']['village'])
    ward: Optional[str] = Field(alias=VOTING_DISTRICTS['county']['ward'])
    local_school: Optional[str] = Field(alias=VOTING_DISTRICTS['county']['local_school_district'])
    library: Optional[str] = Field(alias=VOTING_DISTRICTS['county']['library_district'])
    career_center: Optional[str] = Field(alias=VOTING_DISTRICTS['county']['career_center'])
    education_service_center: Optional[str] = Field(
        alias=VOTING_DISTRICTS['county']['education_service_center'])
    exempted_village_school_district: Optional[str] = Field(
        alias=VOTING_DISTRICTS['county']['exempted_village_school_district'])

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)


class StateDistricts(BaseModel):
    board_of_ed: Optional[str] = Field(alias=VOTING_DISTRICTS['state']['board_of_edu'])
    legislative_lower: Optional[str] = Field(alias=VOTING_DISTRICTS['state']['legislative_lower'])
    legislative_upper: Optional[str] = Field(alias=VOTING_DISTRICTS['state']['legislative_upper'])

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)


class FederalDistricts(BaseModel):
    congressional: Optional[str] = Field(alias=VOTING_DISTRICTS['federal']['congressional'])

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    _clear_blank_strings = root_validator(pre=True, allow_reuse=True)(clear_blank_strings)


class AllAddresses(BaseModel):
    raddress: RegisteredAddress
    maddress: MailingAddress
    raddress_parts: RegisteredAddressParts

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class RecordValidator(BaseModel):
    sec_of_state: SOSInfo
    voter_details: PersonDetails
    address: AllAddresses
    # raddress: RegisteredAddress
    # maddress: MailingAddress
    # raddress_parts: RegisteredAddressParts
    districts: Dict[
        str, VotingPrecinct | CityDistricts | CourtDistricts | CountyDistricts | StateDistricts | FederalDistricts]
    # court_districts: CourtDistricts
    # voting_precinct: VotingPrecinct
    # city_districts: CityDistricts
    # county_districts: CountyDistricts
    # state_districts: StateDistricts
    # federal_districts: FederalDistricts
    vuid: int = Field(alias=VOTER_INFO['vuid'])
    ABSTRACT_HASH: str
    ABSTRACT_UUID: uuid.UUID

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    @root_validator(pre=True)
    @classmethod
    def generate_hash_uuid(cls, values):
        _key_fields = values[VOTER_NAME['last']].lower() + \
                      values[VOTER_NAME['first']].lower() + \
                      str(values[VOTER_INFO['vuid']])
        _record = RecordKeyGenerator(
            record=_key_fields
        )
        values['ABSTRACT_HASH'] = _record.hash
        values['ABSTRACT_UUID'] = _record.uid
        return values

# class ElectionHistory(BaseModel):
#     vuid: str = Field(alias=x['voter-info']['vuid'])
#     y2000: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2000'])
#     y2001: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2001'])
#     y2002: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2002'])
#     y2003: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2003'])
#     y2004: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2004'])
#     y2005: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2005'])
#     y2006: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2006'])
#     y2007: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2007'])
#     y2008: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2008'])
#     y2009: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2009'])
#     y2010: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2010'])
#     y2011: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2011'])
#     y2012: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2012'])
#     y2013: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2013'])
#     y2014: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2014'])
#     y2015: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2015'])
#     y2016: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2016'])
#     y2017: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2017'])
#     y2018: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2018'])
#     y2019: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2019'])
#     y2020: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2020'])
#     y2021: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2021'])
#     y2022: Optional[Dict] = Field(alias=x['ELECTION-DATES']['y2022'])

# [ELECTION-DATES]
# [ELECTION-DATES.Y2000]
# primary.march = ['PRIMARY-03/07/2000']
# general.november = ['GENERAL-11/07/2000']
# [ELECTION-DATES.Y2001]
# special.may = ['SPECIAL-05/08/2001']
# general.november = ['GENERAL-11/06/2001']
# [ELECTION-DATES.Y2002]
# primary.may = ['PRIMARY-05/07/2002']
# general.november = ['GENERAL-11/05/2002']
# [ELECTION-DATES.Y2003]
# special.may = ['SPECIAL-05/06/2003']
# general.november = ['GENERAL-11/04/2003']
# [ELECTION-DATES.Y2004]
# primary.march = ['PRIMARY-03/02/2004']
# general.november = ['GENERAL-11/02/2004']
# [ELECTION-DATES.Y2005]
# special.february = ['SPECIAL-02/08/2005']
# primary.may = ['PRIMARY-05/03/2005']
# primary.september = ['PRIMARY-09/13/2005']
# general.november = ['GENERAL-11/08/2005']
# [ELECTION-DATES.Y2006]
# special.february = ['SPECIAL-02/07/2006']
# primary.may = ['PRIMARY-05/02/2006']
# general.november = ['GENERAL-11/07/2006']
# [ELECTION-DATES.Y2007]
# primary.may = ['PRIMARY-05/08/2007']
# primary.september = ['PRIMARY-09/11/2007']
# general.november = ['GENERAL-11/06/2007']
# primary.november = ['PRIMARY-11/06/2007']
# general.december = ['GENERAL-12/11/2007']
# [ELECTION-DATES.Y2008]
# primary.march = ['PRIMARY-03/04/2008']
# primary.october = ['PRIMARY-10/14/2008']
# general.november = ['GENERAL-11/04/2008', 'GENERAL-11/18/2008']
# [ELECTION-DATES.Y2009]
# primary.may = ['PRIMARY-05/05/2009']
# primary.september = ['PRIMARY-09/08/2009', 'PRIMARY-09/15/2009', 'PRIMARY-09/29/2009']
# general.november = ['GENERAL-11/03/2009']
# [ELECTION-DATES.Y2010]
# primary.may = ['PRIMARY-05/04/2010']
# primary.july = ['PRIMARY-07/13/2010']
# primary.september = ['PRIMARY-09/07/2010']
# general.november = ['GENERAL-11/02/2010']
# [ELECTION-DATES.Y2011]
# primary.may = ['PRIMARY-05/03/2011']
# primary.september = ['PRIMARY-09/13/2011']
# general.november = ['GENERAL-11/08/2011']
# [ELECTION-DATES.Y2012]
# primary.march = ['PRIMARY-03/06/2012']
# general.november = ['GENERAL-11/06/2012']
# [ELECTION-DATES.Y2013]
# primary.may = ['PRIMARY-05/07/2013']
# primary.september = ['PRIMARY-09/10/2013']
# primary.october = ['PRIMARY-10/01/2013']
# general.november = ['GENERAL-11/05/2013']
# [ELECTION-DATES.Y2014]
# primary.may = ['PRIMARY-05/06/2014']
# general.november = ['GENERAL-11/04/2014']
# [ELECTION-DATES.Y2015]
# primary.may = ['PRIMARY-05/05/2015']
# primary.september = ['PRIMARY-09/15/2015']
# general.november = ['GENERAL-11/03/2015']
# [ELECTION-DATES.Y2016]
# primary.march = ['PRIMARY-03/15/2016']
# general.june = ['GENERAL-06/07/2016']
# primary.september = ['PRIMARY-09/13/2016']
# general.november = ['GENERAL-11/08/2016']
# [ELECTION-DATES.Y2017]
# primary.may = ['PRIMARY-05/02/2017']
# primary.september = ['PRIMARY-09/12/2017']
# general.november = ['GENERAL-11/07/2017']
# [ELECTION-DATES.Y2018]
# primary.may = ['PRIMARY-05/08/2018']
# general.august = ['GENERAL-08/07/2018']
# general.november = ['GENERAL-11/06/2018']
# [ELECTION-DATES.Y2019]
# primary.may = ['PRIMARY-05/07/2019']
# primary.september = ['PRIMARY-09/10/2019']
# general.november = ['GENERAL-11/05/2019']
# [ELECTION-DATES.Y2020]
# primary.march = ['PRIMARY-03/17/2020']
# general.november = ['GENERAL-11/03/2020']
# [ELECTION-DATES.Y2021]
# primary.may = ['PRIMARY-05/04/2021']
# primary.august = ['PRIMARY-08/03/2021']
# primary.september = ['PRIMARY-09/14/2021']
# general.november = ['GENERAL-11/02/2021']
# [ELECTION-DATES.Y2022]
# primary.may = ['PRIMARY-05/03/2022']
# primary.august = ['PRIMARY-08/02/2022']
# general.november = ['GENERAL-11/08/2022']
#
# [PARTY-AFFILIATIONS]
# C = 'Constitution Party'
# D = 'Democrat Party'
# E = 'Reform Party'
# G = 'Green Party'
# L = 'Libertarian Party'
# N = 'Natural Law Party'
# R = 'Republican Party'
# S = 'Socialist Party'
# X = 'Voted without declaring party affiliation'
