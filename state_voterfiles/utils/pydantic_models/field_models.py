from __future__ import annotations
from typing import Annotated, Optional, Dict, Any, List
from datetime import date

from pydantic import Field as PydanticField
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber
from pydantic.types import PastDate
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig


# TODO: Integrate Strawberry GraphQL types into the models (https://strawberry.rocks/docs/integrations/pydantic)

# TODO: Build the table name off the state_schema and then name each table accordingly.
#  Will need to consider how to do this for target and voter file data.

# TODO: Figure out where and how to build linked models, specifically for addresses.

class ValidatorBaseModel(ValidatorConfig):
    id: Optional[int] = PydanticField(default=None)


class PersonName(ValidatorBaseModel):
    prefix: Optional[str] = PydanticField(default=None)
    first: str = PydanticField(...)
    last: str = PydanticField(...)
    middle: Optional[str] = PydanticField(default=None)
    suffix: Optional[str] = PydanticField(default=None)
    dob: Optional[PastDate] = PydanticField(default=None)
    gender: Optional[str] = PydanticField(default=None, max_length=1)
    other_fields: Optional[Dict[str, Any]] = PydanticField(default=None)


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


class ValidatedPhoneNumber(ValidatorBaseModel):
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
    type: str = PydanticField(..., description="Type of district (e.g., 'city', 'county', 'court', 'state', 'federal')")
    name: Optional[str] = PydanticField(default=None, description="Name of the district")
    number: Optional[str] = PydanticField(default=None, description="Number or ID of the district")
    attributes: Dict[str, Any] = PydanticField(default_factory=dict, description="Additional attributes specific to the district type")


# class GovernmentDistricts(ValidatorBaseModel):
#     person_id: Optional[int] = PydanticField(default=None, description="ID of the associated voter")
#     districts: Dict[str, District] = PydanticField(default_factory=None, description="Dictionary of districts associated with the voter")
#

class VendorTags(ValidatorBaseModel):
    vendor: str = PydanticField(..., description="Name of the vendor")
    tags: Dict[str, Any] = PydanticField(..., description="List of tags associated with the vendor")


class InputData(ValidatorBaseModel):
    input_data: Annotated[Optional[InputData], PydanticField(default=None)]
    original_data: Annotated[Dict[str, Any], PydanticField(...)]
    renamed_data: Annotated[Dict[str, Any], PydanticField(...)]
    corrections: Annotated[Dict[str, Any], PydanticField(...)]
    settings: Annotated[Dict[str, Any], PydanticField(...)]
    date_format: Annotated[str | List[str], PydanticField(...)]

# class CityDistricts(ValidatorConfig):
#     id: Annotated[Optional[int], PydanticField(default=None)]
#     name: Annotated[
#         Optional[str],
#         PydanticField(default=None)
#     ]
#     school_district: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#
#
# class CountyDistricts(ValidatorConfig):
#     id: Annotated[Optional[int], PydanticField(default=None)]
#     number: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#     id: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#     township: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#     village: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#     ward: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#     local_school_district: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#     library_district: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#     career_center: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#     education_service_center: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#     exempted_village_school_district: Annotated[
#         Optional[str],
#         PydanticField(
#             default=None
#         )
#     ]
#
#
# class CourtDistricts(ValidatorConfig):
#     id: Annotated[Optional[int], PydanticField(default=None)]
#     municipal: Annotated[Optional[str], PydanticField(default=None)]
#     county: Annotated[Optional[str], PydanticField(default=None)]
#     appellate: Annotated[Optional[str], PydanticField(default=None)]
#
#
# class StateDistricts(ValidatorConfig):
#     id: Annotated[Optional[int], PydanticField(default=None)]
#     board_of_education: Annotated[
#         Optional[int],
#         PydanticField(
#             default=None,
#         )
#     ]
#     legislative_lower: Annotated[
#         Optional[int],
#         PydanticField(
#             default=None,
#         )
#     ]
#     legislative_upper: Annotated[
#         Optional[int],
#         PydanticField(
#             default=None,
#         )
#     ]
#
#
# class FederalDistricts(ValidatorConfig):
#     id: Annotated[Optional[int], PydanticField(default=None)]
#     congressional: Annotated[
#         Optional[int],
#         PydanticField(
#             default=None,
#         )
#     ]
#
#
# class Districts(ValidatorConfig):
#     id: Annotated[Optional[int], PydanticField(default=None)]
#     court: Annotated[
#         Optional[CourtDistricts],
#         PydanticField(
#             default=None,
#
#         )
#     ]
#     city: Annotated[
#         Optional[CityDistricts],
#         PydanticField(
#             default=None,
#
#         )
#     ]
#     county: Annotated[
#         Optional[CountyDistricts],
#         PydanticField(
#             default=None,
#
#         )
#     ]
#     state: Annotated[
#         Optional[StateDistricts],
#         PydanticField(
#             default=None,
#
#         )
#     ]
#
#     federal: Annotated[
#         Optional[FederalDistricts],
#         PydanticField(
#             default=None,
#
#         )]


class CustomFields(ValidatorConfig):
    fields: Annotated[
        Optional[Dict[str, Any]],
        PydanticField(
            default=None,
        )
    ]


class Election(ValidatorBaseModel):
    election_type: Annotated[str, PydanticField(description="Type of election (e.g., 'general', 'primary')")]
    year: Annotated[str, PydanticField(description="Year of election", min_length=4, max_length=4)]
    vote_date: Annotated[Optional[date], PydanticField(default=None, description="Date person voted")]
    vote_method: Annotated[str, PydanticField(description="Method of voting (e.g., 'mail', 'in-person')")]
    primary_party: Annotated[Optional[str], PydanticField(default=None, description="Party affiliation for primary elections")]


class RecordBaseModel(ValidatorBaseModel):
    name: Annotated[Optional[PersonName], PydanticField(default=None)]
    voter_registration: Annotated[Optional[VoterRegistration], PydanticField(default=None)]
    # residential_address: Annotated[Optional[Address], PydanticField(default=None)]
    # mailing_address: Annotated[Optional[Address], PydanticField(default=None)]
    address_list: Annotated[Optional[List[Address]], PydanticField(default_factory=list)]
    districts: Annotated[Optional[List[District]], PydanticField(default=None)]
    phone: Annotated[Optional[List[ValidatedPhoneNumber]], PydanticField(default=None)]
    vendors: Annotated[Optional[List[VendorTags]], PydanticField(default=None)]
    election_history: Annotated[Optional[List[Election]], PydanticField(
        default=None,
        description='List of election history records'
    )
    ]
    unassigned: Annotated[Optional[Dict[str, Any]], PydanticField(default=None)]
    vep_keys: Annotated[Optional[VEPMatch], PydanticField(default_factory=VEPMatch)]
    corrected_errors: Annotated[Dict[str, Any], PydanticField(default_factory=dict)]
    input_data: Annotated[Optional[InputData], PydanticField(default=None)]
