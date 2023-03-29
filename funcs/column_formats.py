from dataclasses import dataclass, field
from utils.toml_reader import TomlReader
from pathlib import Path
from typing import ClassVar


# ohio_cols = TomlReader(Path(__file__).parent.parent / 'state_fields' / 'ohio-fields.toml').data


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
