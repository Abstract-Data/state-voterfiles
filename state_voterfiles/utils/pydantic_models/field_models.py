from __future__ import annotations
from typing import Annotated, Optional, Dict, Any, List, ClassVar, Set
from datetime import date

from pydantic import Field as PydanticField
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber
from pydantic.types import PastDate
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
from state_voterfiles.utils.pydantic_models.election_details import VotedInElection
from state_voterfiles.utils.funcs.record_keygen import RecordKeyGenerator


# TODO: Integrate Strawberry GraphQL types into the models (https://strawberry.rocks/docs/integrations/pydantic)

# TODO: Build the table name off the state_schema and then name each table accordingly.
#  Will need to consider how to do this for target and voter file data.

# TODO: Figure out where and how to build linked models, specifically for addresses.

class ValidatorBaseModel(ValidatorConfig):
    id: Optional[int] = PydanticField(default=None)


class PersonName(ValidatorBaseModel):
    id: Optional[str] = PydanticField(default=None)
    prefix: Optional[str] = PydanticField(default=None)
    first: str = PydanticField(...)
    last: str = PydanticField(...)
    middle: Optional[str] = PydanticField(default=None)
    suffix: Optional[str] = PydanticField(default=None)
    dob: Optional[PastDate] = PydanticField(default=None)
    gender: Optional[str] = PydanticField(default=None, max_length=1)
    other_fields: Optional[Dict[str, Any]] = PydanticField(default=None)

    def __hash__(self):
        return hash(self.id)

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def generate_hash_key(self) -> str:
        return RecordKeyGenerator.generate_static_key((self.first, self.last, self.dob))


class VoterRegistration(ValidatorBaseModel):
    vuid: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    edr: Annotated[
        Optional[date],
        PydanticField(default=None),
    ]
    status: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    county: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    attributes: Annotated[
        Optional[Dict[str, Any]],
        PydanticField(default=None)
    ]


class Address(ValidatorBaseModel):
    """
    This should be used for all addresses, you'll need to pass a dictionary of the address fields to the model, versus all values
    """
    id: Optional[str] = PydanticField(default=None)
    address_type: Annotated[
        Optional[str],
        PydanticField(default=None)]
    address1: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    address2: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    city: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    state: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    zipcode: Annotated[
        Optional[str],
        PydanticField(
            pattern=r'^\d{5}(-\d{4})?$'
        ),
        PydanticField(default=None)
    ]
    zip5: Annotated[
        Optional[str],
        PydanticField(default=None, max_length=5, min_length=5)
    ]
    zip4: Annotated[
        Optional[str],
        PydanticField(default=None, max_length=4, min_length=4)
    ]
    county: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    country: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    standardized: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]

    address_parts: Annotated[
        Optional[Dict[str, Any]],
        PydanticField(default=None)
    ]

    address_key: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    is_mailing: Annotated[
        Optional[bool],
        PydanticField(default=None),
    ]
    other_fields: Annotated[
        Optional[Dict[str, Any]],
        PydanticField(default=None)
    ]

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def generate_hash_key(self) -> str:
        if not self.standardized:
            raise ValueError("Address must be standardized before generating a hash key.")
        return RecordKeyGenerator.generate_static_key(self.standardized)

    def update(self, other: Address):
        if other.address1 and not self.address1:
            self.address1 = other.address1
        if other.address2 and not self.address2:
            self.address2 = other.address2
        if other.city and not self.city:
            self.city = other.city
        if other.state and not self.state:
            self.state = other.state
        if other.zipcode and not self.zipcode:
            self.zipcode = other.zipcode
        if other.zip5 and not self.zip5:
            self.zip5 = other.zip5
        if other.zip4 and not self.zip4:
            self.zip4 = other.zip4
        if other.county and not self.county:
            self.county = other.county
        if other.country and not self.country:
            self.country = other.country
        if other.standardized and not self.standardized:
            self.standardized = other.standardized
        if other.address_parts and not self.address_parts:
            self.address_parts = other.address_parts
        if other.address_key and not self.address_key:
            self.address_key = other.address_key
        if other.is_mailing and not self.is_mailing:
            self.is_mailing = other.is_mailing
        if other.other_fields:
            self.other_fields.update(other.other_fields)


class ValidatedPhoneNumber(ValidatorBaseModel):
    id: Optional[str] = PydanticField(default=None)
    phone_type: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    phone: Annotated[
        PydanticPhoneNumber,
        PydanticField()
    ]
    areacode: Annotated[
        str,
        PydanticField(),
    ]
    number: Annotated[
        str,
        PydanticField(),
    ]
    reliability: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    other_fields: Annotated[
        Optional[Dict[str, Any]],
        PydanticField(default_factory=dict)
    ]

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def generate_hash_key(self) -> str:
        return RecordKeyGenerator.generate_static_key(self.phone)


class VEPMatch(ValidatorBaseModel):
    uuid: Annotated[
        Optional[str],
        PydanticField(default=None),
    ]
    long: Annotated[
        Optional[str],
        PydanticField(default=None),
    ]
    short: Annotated[
        Optional[str],
        PydanticField(default=None),
    ]
    name_dob: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    addr_text: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    addr_key: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    full_key: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    full_key_hash: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    best_key: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    uses_mailzip: Annotated[
        Optional[bool],
        PydanticField(default=None)
    ]


class District(ValidatorBaseModel):
    id: Optional[str] = PydanticField(default=None)
    state_abbv: Annotated[
        Optional[str],
        PydanticField(
            default=None,
            description="State abbreviation"
        )
    ]
    city: Annotated[
        Optional[str],
        PydanticField(
            default=None,
            description="City name"
        )
    ]
    county: Annotated[
        Optional[str],
        PydanticField(
            default=None,
            description="County name"
        )
    ]
    type: Annotated[
        str,
        PydanticField(
            ...,
            description="Type of district (e.g., 'city', 'county', 'court', 'state', 'federal')"
        )
    ]
    name: Annotated[
        Optional[str],
        PydanticField(
            default=None,
            description="Name of the district"
        )
    ]
    number: Annotated[
        Optional[str],
        PydanticField(
            default=None,
            description="Number or ID of the district"
        )
    ]
    attributes: Annotated[
        Dict[str, Any],
        PydanticField(
            default_factory=dict,
            description="Additional attributes specific to the district type"
        )
    ]
    record_associations: Annotated[
        Optional[List[RecordDistrict]],
        PydanticField(
            default=None
        )
    ]

    def __init__(self, **data):
        super().__init__(**data)
        _make_key = RecordKeyGenerator.generate_static_key
        if self.city:
            self.id = _make_key((self.state_abbv, self.city, self.type, self.name, self.number))
        elif self.county:
            self.id = _make_key((self.state_abbv, self.county, self.type, self.name, self.number))
        else:
            self.id = _make_key((self.state_abbv, self.type, self.name, self.number))

    def __hash__(self):
        return hash(self.id)

    def update(self, other: District):
        if other.city and not self.city:
            self.city = other.city
        if other.county and not self.county:
            self.county = other.county
        if other.name and not self.name:
            self.name = other.name
        if other.number and not self.number:
            self.number = other.number
        if other.attributes:
            self.attributes.update(other.attributes)


class RecordDistrict(ValidatorBaseModel):

    district_id: Annotated[Optional[str], PydanticField(default=None, description="ID of the district")]
    district: Annotated[Optional[District], PydanticField(default=None, description="District information")]
    record_id: Annotated[Optional[int], PydanticField(default=None, description="ID of the record")]
    record: Annotated[Optional[RecordBaseModel], PydanticField(default=None, description="Record information")]


class VendorName(ValidatorBaseModel):
    id: Optional[str] = PydanticField(default=None)
    name: Annotated[str, PydanticField(...)]

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def generate_hash_key(self) -> str:
        return RecordKeyGenerator.generate_static_key(self.name)

    def __hash__(self):
        return hash(self.id)


class VendorTags(ValidatorBaseModel):
    vendor_id: str = PydanticField(..., description="Name of the vendor")
    tags: Dict[str, Any] = PydanticField(..., description="List of tags associated with the vendor")


class InputData(ValidatorBaseModel):
    input_data: Annotated[Optional[InputData], PydanticField(default=None)]
    original_data: Annotated[Dict[str, Any], PydanticField(...)]
    renamed_data: Annotated[Dict[str, Any], PydanticField(...)]
    corrections: Annotated[Dict[str, Any], PydanticField(...)]
    settings: Annotated[Dict[str, Any], PydanticField(...)]
    date_format: Annotated[str | List[str], PydanticField(...)]


class CustomFields(ValidatorConfig):
    fields: Annotated[
        Optional[Dict[str, Any]],
        PydanticField(
            default=None,
        )
    ]


# class Election(ValidatorBaseModel):
#     election_type: Annotated[str, PydanticField(description="Type of election (e.g., 'general', 'primary')")]
#     year: Annotated[int, PydanticField(..., description="Year of election")]
#     vote_date: Annotated[Optional[date], PydanticField(default=None, description="Date person voted")]
#     vote_method: Annotated[
#         Optional[str], PydanticField(default=None, description="Method of voting (e.g., 'mail', 'in-person')")]
#     primary_party: Annotated[
#         Optional[str], PydanticField(default=None, description="Party affiliation for primary elections")]
#     attributes: Annotated[Dict[str, Any], PydanticField(default_factory=dict,
#                                                         description="Additional attributes specific to the election type")]


class DataSource(ValidatorBaseModel):
    file: Annotated[str, PydanticField(..., description="Name of the file")]
    processed_date: Annotated[date, PydanticField(default=date.today(), description="Date the file was processed")]

    def __hash__(self):
        return hash(self.file)


class RecordBaseModel(ValidatorBaseModel):
    name: Annotated[Optional[PersonName], PydanticField(default=None)]
    voter_registration: Annotated[Optional[VoterRegistration], PydanticField(default=None)]
    address_list: Annotated[Optional[List[Address]], PydanticField(default_factory=list)]
    districts: Annotated[Optional[List[RecordDistrict]], PydanticField(default=None)]
    phone: Annotated[Optional[List[ValidatedPhoneNumber]], PydanticField(default=None)]
    vendors: Annotated[Optional[List[VendorTags]], PydanticField(default=None)]
    election_history: Annotated[
        Optional[List[VotedInElection]],
        PydanticField(
            default=None,
            description='List of election history records'
        )
    ]
    unassigned: Annotated[Optional[Dict[str, Any]], PydanticField(default=None)]
    vep_keys: Annotated[Optional[VEPMatch], PydanticField(default_factory=VEPMatch)]
    corrected_errors: Annotated[Dict[str, Any], PydanticField(default_factory=dict)]
    input_data: Annotated[Optional[InputData], PydanticField(default=None)]
    data_sources: Annotated[List[DataSource], PydanticField(default=[])]
