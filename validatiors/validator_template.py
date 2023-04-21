# import hashlib
# import uuid
# from funcs.record_keygen import RecordKeyGenerator
# from pydantic import BaseModel, ValidationError, validator, Field, root_validator, conint
# from typing import Optional, Annotated, Dict, List
# from datetime import date, datetime
# import zipcodes
# from utils.toml_reader import StateConfig
#
# # TODO: Fix StateConfig.data to be a dict of dicts
# # TODO: Check to make sure the ElectionHistory validator is working as needed.
# class ValidatorTemplate(BaseModel):
#     vuid: str = Field(alias=StateConfig.data['PERSON-DETAILS.voter-info']['vuid'])
#     edr: date = Field(alias=TomlReader.data['PERSON-DETAILS.voter-info']['registration_date'])
#     status: str = Field(alias=TomlReader.data['PERSON-DETAILS.voter-info']['registration_status'])
#     lname: str = Field(alias=TomlReader.data['PERSON-DETAILS.name']['last'])
#     fname: str = Field(alias=TomlReader.data['PERSON-DETAILS.name']['first'])
#     mname: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.name']['middle'])
#     sfx: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.name']['suffix'])
#     dob: date = Field(alias=TomlReader.data['PERSON-DETAILS.voter-info']['dob'])
#     radr1: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.residence']['address1'])
#     radr2: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.residence']['address2'])
#     rcity: str = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.residence']['city'])
#     rstate: str = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.residence']['state'])
#     rzip: conint(ge=0, le=99999) = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.residence']['zip5'])
#     rzip4: Optional[Annotated[int, Field(ge=0, le=9999)]] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.residence']['zip4'])
#     rcountry: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.residence']['country'])
#     rpostal_code: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.residence']['postal_code'])
#     rhnum: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['house_number'])
#     rdesig: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['house_direction'])
#     rstname: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['street_name'])
#     rsttype: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['street_type'])
#     rstsfx: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['street_suffix'])
#     runum: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['unit_number'])
#     rutype: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['unit_type'])
#     # rcity: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['city'])
#     # rstate: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['state'])
#     # rzip: Optional[Annotated[int, Field(ge=0, le=99999)]] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['zip'])
#     # rzip4: Optional[Annotated[int, Field(ge=0, le=9999)]] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.parts.residence']['zip4'])
#
#     maddr1: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.mail']['address1'])
#     maddr2: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.mail']['address2'])
#     mcity: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.mail']['city'])
#     mstate: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.mail']['state'])
#     mzip: Optional[Annotated[int, Field(ge=0, le=99999)]] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.mail']['zip5'])
#     mzip4: Optional[Annotated[int, Field(ge=0, le=9999)]] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.mail']['zip4'])
#     mcountry: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.mail']['country'])
#     mpostal_code: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.ADDRESS.mail']['postal_code'])
#
#     municipal_court_district: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['municipal_court_district'])
#     court_of_appeals: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['court_of_appeals'])
#     local_school_district: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['local_school_district'])
#
#     precinct_name: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['precinct']['name'])
#     precinct_code: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['precinct']['code'])
#
#     city_district: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['city']['district'])
#     city_school_district: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['city']['school_district'])
#
#     county_district_number: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['county']['number'])
#     county_district_id: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['county']['id'])
#     county_district_township: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['county']['township'])
#     county_district_village: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['county']['village'])
#     county_district_ward: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['county']['ward'])
#     county_district_library: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['county']['library_district'])
#     county_district_career_center: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['county']['career_center'])
#     county_district_court: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['county']['court_district'])
#     county_district_education_service_center: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['county']['education_service_center'])
#     county_district_exempted_village_school_district: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['county']['exempted_village_school_district'])
#
#     state_board_of_education: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['state']['board_of_edu'])
#     state_representative_district: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['state']['lower_chamber'])
#     state_senate_district: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['state']['upper_chamber'])
#
#     congressional_district: Optional[str] = Field(alias=TomlReader.data['PERSON-DETAILS.VOTING-DISTRICTS']['federal']['congressional'])
#
#     class Config:
#         allow_population_by_field_name = True
#         orm_mode = True
#
# class ElectionHistory(BaseModel):
#     vuid: str = Field(alias=TomlReader.data['PERSON-DETAILS.voter-info']['vuid'])
#     y2000: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2000'])
#     y2001: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2001'])
#     y2002: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2002'])
#     y2003: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2003'])
#     y2004: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2004'])
#     y2005: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2005'])
#     y2006: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2006'])
#     y2007: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2007'])
#     y2008: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2008'])
#     y2009: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2009'])
#     y2010: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2010'])
#     y2011: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2011'])
#     y2012: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2012'])
#     y2013: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2013'])
#     y2014: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2014'])
#     y2015: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2015'])
#     y2016: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2016'])
#     y2017: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2017'])
#     y2018: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2018'])
#     y2019: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2019'])
#     y2020: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2020'])
#     y2021: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2021'])
#     y2022: Optional[Dict] = Field(alias=TomlReader.data['ELECTION-DATES.y2022'])


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