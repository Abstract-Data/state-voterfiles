from typing import Optional, Annotated, List, Dict, Any

from pydantic import Field as PydanticField

from state_voterfiles.utils.pydantic_models.base import ValidatorBaseModel
from state_voterfiles.utils.pydantic_models.field_models import (
    PersonName,
    VoterRegistration,
    VendorTags,
    VEPMatch,
    InputData,
    DataSource
)
from state_voterfiles.utils.pydantic_models.election_details import VotedInElection
from state_voterfiles.utils.pydantic_models.list_models import (
    RecordAddressList,
    RecordDistrictList,
    RecordPhoneNumberList
)


class RecordBaseModel(ValidatorBaseModel):
    name: Annotated[PersonName, PydanticField(default=PersonName)]
    voter_registration: Annotated[Optional[VoterRegistration], PydanticField(default=VoterRegistration)]
    address_list: Annotated[Optional[RecordAddressList], PydanticField(default_factory=RecordAddressList)]
    districts: Annotated[Optional[RecordDistrictList], PydanticField(default=RecordDistrictList)]
    phone: Annotated[Optional[RecordPhoneNumberList], PydanticField(default=RecordPhoneNumberList)]
    vendors: Annotated[Optional[List[VendorTags]], PydanticField(default=None)]
    election_history: Annotated[
        Optional[List[VotedInElection]],
        PydanticField(
            default_factory=list,
            description='List of election history records'
        )
    ]
    unassigned: Annotated[Optional[Dict[str, Any]], PydanticField(default=None)]
    vep_keys: Annotated[VEPMatch, PydanticField(default_factory=VEPMatch)]
    corrected_errors: Annotated[Dict[str, Any], PydanticField(default_factory=dict)]
    input_data: Annotated[InputData, PydanticField(default_factory=InputData)]
    data_sources: Annotated[List[DataSource], PydanticField(default=[])]