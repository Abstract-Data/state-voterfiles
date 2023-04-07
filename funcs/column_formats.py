from dataclasses import dataclass, field
from utils.toml_reader import TomlReader
from pathlib import Path
from typing import ClassVar


"""
=========================
==== DESCRIPTION ========
=========================

Each object feeds into the `VoterInfo` object, which turns each column within a states .toml into reference vars. 

EXAMPLE:
{'_VoterInfo__state': PosixPath('/Users/johneakin/PyCharmProjects/state-voterfiles/state_fields/texas-fields.toml'),
 '_data': {'voter-info': {'vuid': 'VUID',
   'registration_date': 'EDR',
   'registration_status': 'STATUS',
   'political_party': '',
   'dob': 'DOB'},
  'name': {'last': 'LNAME',
   'first': 'FNAME',
   'middle': 'MNAME',
   'suffix': 'SFX'},
  'ADDRESS': {'residence': {'address1': 'RESIDENTIAL_ADDRESS1',
    'address2': 'RESIDENTIAL_SECONDARY_ADDR',
    'city': 'RESIDENTIAL_CITY',
    'state': 'RESIDENTIAL_STATE',
    'zip5': 'RESIDENTIAL_ZIP',
    'zip4': 'RESIDENTIAL_ZIP_PLUS4',
    'country': 'RESIDENTIAL_COUNTRY',
    'postal_code': 'RESIDENTIAL_POSTALCODE'},
   'parts': {'residence': {'house_number': 'RHNUM',
     'house_direction': 'RDESIG',
     'street_name': 'RSTNAME',
     'street_type': 'RSTTYPE',
     'street_suffix': 'RSTSFX',
     'unit_number': 'RUNUM',
     'unit_type': 'RUTYPE',
     'city': 'RCITY',
     'state': 'TX',
     'zip': 'RZIP',
     'zip4': 'RZIP4'}},
   'mail': {'address1': 'MADR1',
    'address2': 'MADR2',
    'city': 'MCITY',
    'state': 'MST',
    'zip5': 'MZIP',
    'zip4': 'MZIP4',
    'country': '',
    'postal_code': ''}},
  'VOTING-DISTRICTS': {'municipal_court_district': '',
   'court_of_appeals': '',
   'local_school_district': '',
   'precinct': {'name': '', 'code': ''},
   'city': {'name': '', 'school_district': ''},
   'county': {'number': 'COUNTY_NUMBER',
    'id': 'COUNTY_ID',
    'township': 'TOWNSHIP',
    'village': 'VILLAGE',
    'ward': 'WARD',
    'library_district': 'LIBRARY',
    'career_center': 'CAREER_CENTER',
    'court_district': 'COUNTY_COURT_DISTRICT',
    'education_service_center': 'EDU_SERVICE_CENTER_DISTRICT',
    'exempted_village_school_district': 'EXEMPTED_VILL_SCHOOL_DISTRICT'},
   'state': {'board_of_edu': 'STATE_BOARD_OF_EDUCATION',
    'lower_chamber': 'STATE_REPRESENTATIVE_DISTRICT',
    'upper_chamber': 'STATE_SENATE_DISTRICT'},
   'federal': {'congressional': 'CONGRESSIONAL_DISTRICT'}}},
 '_elections': {'Y2000': {'primary': {'march': ''},
   'general': {'november': ''}},
  'Y2001': {'special': {'may': ''}, 'general': {'november': ''}},
  'Y2002': {'primary': {'may': ''}, 'general': {'november': ''}},
  'Y2003': {'special': {'may': ''}, 'general': {'november': ''}},
  'Y2004': {'primary': {'march': ''}, 'general': {'november': ''}},
  'Y2005': {'special': {'february': ''},
   'primary': {'may': '', 'september': ''},
   'general': {'november': ''}},
  'Y2006': {'special': {'february': ''},
   'primary': {'may': ''},
   'general': {'november': ''}},
  'Y2007': {'primary': {'may': '', 'september': '', 'november': ''},
   'general': {'november': '', 'december': ''}},
  'Y2008': {'primary': {'march': '', 'october': ''},
   'general': {'november': ''}},
  'Y2009': {'primary': {'may': '', 'september': ''},
   'general': {'november': ''}},
  'Y2010': {'primary': {'may': '', 'july': ''}, 'general': {'november': ''}},
  'Y2011': {'primary': {'may': '', 'september': ''},
   'general': {'november': ''}},
  'Y2012': {'primary': {'march': ''}, 'general': {'november': ''}},
  'Y2013': {'primary': {'may': '', 'september': '', 'october': ''},
   'general': {'november': ''}},
  'Y2014': {'primary': {'may': ''}, 'general': {'november': ''}},
  'Y2015': {'primary': {'may': '', 'september': ''},
   'general': {'november': ''}},
  'Y2016': {'primary': {'march': '', 'september': ''},
   'general': {'june': '', 'november': ''}},
  'Y2017': {'primary': {'may': '', 'september': ''},
   'general': {'november': ''}},
  'Y2018': {'primary': {'may': ''}, 'general': {'august': '', 'november': ''}},
  'Y2019': {'primary': {'may': '', 'september': ''},
   'general': {'november': ''}},
  'Y2020': {'primary': {'march': ''}, 'general': {'november': ''}},
  'Y2021': {'primary': {'may': '', 'august': '', 'september': ''},
   'general': {'november': ''}},
  'Y2022': {'primary': {'may': '', 'august': ''},
   'general': {'november': ''}}},
 '_party': {'C': '',
  'D': '',
  'E': '',
  'G': '',
  'L': '',
  'N': '',
  'R': '',
  'S': '',
  'X': ''},
 'voter_info': SOSVoterInfo(vuid='VUID', registration_date='EDR', registration_status='STATUS', political_party='', dob='DOB'),
 'name': VoterName(first='FNAME', middle='MNAME', last='LNAME', suffix='SFX'),
 'registration_address_parts': VoterAddressParts(house_number='RHNUM', house_direction='RDESIG', street_name='RSTNAME', street_type='RSTTYPE', street_suffix='RSTSFX', unit_number='RUNUM', unit_type='RUTYPE', city='RCITY', state='TX', zip='RZIP', zip4='RZIP4', address_obj=VoterAddress(address1='RHNUM RDESIG RSTNAME RSTTYPE RSTSFX', address2='RUTYPE RUNUM', city='RCITY', state='TX', zip5='RZIP', zip4='RZIP4', country='', postal_code='')),
 'registration_address': VoterAddress(address1='RESIDENTIAL_ADDRESS1', address2='RESIDENTIAL_SECONDARY_ADDR', city='RESIDENTIAL_CITY', state='RESIDENTIAL_STATE', zip5='RESIDENTIAL_ZIP', zip4='RESIDENTIAL_ZIP_PLUS4', country='RESIDENTIAL_COUNTRY', postal_code='RESIDENTIAL_POSTALCODE'),
 'mailing_address': VoterAddress(address1='MADR1', address2='MADR2', city='MCITY', state='MST', zip5='MZIP', zip4='MZIP4', country='', postal_code=''),
 'precinct': VoterPrecinct(name='', code=''),
 'city': VoterCity(name='', school_district=''),
 'county': VoterCounty(number='COUNTY_NUMBER', id='COUNTY_ID', township='TOWNSHIP', village='VILLAGE', ward='WARD', library_district='LIBRARY', career_center='CAREER_CENTER', court_district='COUNTY_COURT_DISTRICT', education_service_center='EDU_SERVICE_CENTER_DISTRICT', exempted_village_school_district='EXEMPTED_VILL_SCHOOL_DISTRICT'),
 'state': VoterState(board_of_edu='STATE_BOARD_OF_EDUCATION', lower_chamber='STATE_REPRESENTATIVE_DISTRICT', upper_chamber='STATE_SENATE_DISTRICT'),
 'federal': VoterFederal(congressional='CONGRESSIONAL_DISTRICT')}
"""


@dataclass
class SOSVoterInfo:
    vuid: str
    registration_date: str
    registration_status: str
    political_party: str
    dob: str

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True


@dataclass
class VoterName:
    first: str
    middle: str
    last: str
    suffix: str


@dataclass
class VoterAddress:
    address1: str
    address2: str
    city: str
    state: str
    zip5: str
    zip4: str
    country: str
    postal_code: str


@dataclass
class VoterAddressParts:
    house_number: str
    house_direction: str
    street_name: str
    street_type: str
    street_suffix: str
    unit_number: str
    unit_type: str
    city: str
    state: str
    zip: str
    zip4: str
    address_obj: VoterAddress = field(init=False)

    def __post_init__(self):
        self.address_obj = VoterAddress(
            address1=f'{self.house_number} {self.house_direction} {self.street_name} {self.street_type} {self.street_suffix}',
            address2=f'{self.unit_type} {self.unit_number}',
            city=self.city,
            state=self.state,
            zip5=self.zip,
            zip4=self.zip4,
            postal_code='',
            country=''
        )


@dataclass
class VoterPrecinct:
    name: str
    code: str


@dataclass
class VoterCity:
    name: str
    school_district: str


@dataclass
class VoterCounty:
    number: str
    id: str
    township: str
    village: str
    ward: str
    library_district: str
    career_center: str
    court_district: str
    education_service_center: str
    exempted_village_school_district: str


@dataclass
class VoterState:
    board_of_edu: str
    lower_chamber: str
    upper_chamber: str


@dataclass
class VoterFederal:
    congressional: str


@dataclass
class VoterDistricts:
    precinct: str
    city: str
    county: str
    state: str
    federal: str


@dataclass
class Election:
    _year: int
    election_type: str
    month: str
    date: str

    @property
    def year(self):
        return self._year[-4:]


@dataclass
class VoterInfo:
    __state: Path

    @property
    def _state(self):
        return TomlReader(self.__state).data

    def __post_init__(self):
        self._data = self._state['PERSON-DETAILS']
        self._elections = self._state['ELECTION-DATES']
        self._party = self._state['PARTY-AFFILIATIONS']
        self.voter_info: SOSVoterInfo = SOSVoterInfo(**self._data['voter-info'])
        self.name: VoterName = VoterName(**self._data['name'])
        self.registration_address_parts: VoterAddressParts = VoterAddressParts(**self._data['ADDRESS']['parts']['residence'])
        self.registration_address: VoterAddress = VoterAddress(**self._data['ADDRESS']['residence'])
        self.mailing_address: VoterAddress = VoterAddress(**self._data['ADDRESS']['mail'])
        self.precinct: VoterPrecinct = VoterPrecinct(**self._data['VOTING-DISTRICTS']['precinct'])
        self.city: VoterCity = VoterCity(**self._data['VOTING-DISTRICTS']['city'])
        self.county: VoterCounty = VoterCounty(**self._data['VOTING-DISTRICTS']['county'])
        self.state: VoterState = VoterState(**self._data['VOTING-DISTRICTS']['state'])
        self.federal: VoterFederal = VoterFederal(**self._data['VOTING-DISTRICTS']['federal'])

    @property
    def elections(self):
        election_list = []
        for year in self._elections:
            for election_type in self._elections[year]:
                for month in self._elections[year][election_type]:
                    for each_election in self._elections[year][election_type][month]:
                        election_date = Election(
                            _year=year,
                            election_type=election_type,
                            month=month,
                            date=each_election
                        )
                        election_list.append(election_date)
        return election_list
