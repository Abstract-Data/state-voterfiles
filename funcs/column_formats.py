from dataclasses import dataclass
from utils.toml_reader import TomlReader
from pathlib import Path
from typing import Annotated, Dict

data = TomlReader(Path(__file__).parent.parent / 'state_formatting' / 'ohio-voter-format.toml').data


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
    _data = data['PERSON-DETAILS']
    _elections = data['ELECTION-DATES']
    _party = data['PARTY-AFFILIATIONS']

    def __post_init__(self):
        self.voter_info: SOSVoterInfo = SOSVoterInfo(**self._data['voter-info'])
        self.name: VoterName = VoterName(**self._data['name'])
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


ohio = VoterInfo()


