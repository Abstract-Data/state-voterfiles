from __future__ import annotations
from typing import Optional, Dict, Annotated, Any, Type, List
from pydantic import (
    Field as PydanticField,
    model_validator
)
from pydantic_core import PydanticCustomError
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
from state_voterfiles.utils.pydantic_models.field_models import (
    PersonName,
    VoterRegistration,
    Address,
    ValidatedPhoneNumber,
    VEPMatch,
    District,
    CustomFields,
    VendorTags,
    InputData,
    Election
)


class RecordValidatorABC(ValidatorConfig):
    name: Annotated[
        PersonName,
        PydanticField(
            ...
        )
    ]
    voter_registration: Annotated[
        Optional[VoterRegistration],
        PydanticField(
            default=None
        )
    ]
    address_list: Annotated[
        Optional[List[Address]],
        PydanticField(
            default=None
        )
    ]
    # residential_address: Annotated[
    #     Optional[Address],
    #     PydanticField(default=None)
    # ]
    # mailing_address: Annotated[
    #     Optional[Address],
    #     PydanticField(
    #         default=None
    #     )
    # ]
    districts: Annotated[
        Optional[List[District]],
        PydanticField(
            default=None
        )
    ]
    election_history: Annotated[
        Optional[List[Election]],
        PydanticField(
            default=None,
            description='List of election history records'
        )
    ]
    vep_keys: Annotated[
        VEPMatch,
        PydanticField(
            ...
        )
    ]
    phone: Annotated[
        Optional[List[ValidatedPhoneNumber]],
        PydanticField(
            default=None
        )
    ]
    vendors: Annotated[
        Optional[List[VendorTags]],
        PydanticField(
            default=None,
        )
    ]

    input_data: Annotated[
        InputData,
        PydanticField(
            ...
        )
    ]
    state: Annotated[
        Optional[str],
        PydanticField(
            default=None
        )
    ]

    @model_validator(mode='after')
    def set_default_classes(self):
        if not self.vep_keys:
            raise PydanticCustomError(
                'vep_match_missing',
                'VEP Match object is missing',
                None
            )
        return self
