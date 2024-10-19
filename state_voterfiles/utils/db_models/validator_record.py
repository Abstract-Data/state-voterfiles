
from typing import Dict, Any, Optional

from sqlmodel import Field as SQLModelField

from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
from state_voterfiles.utils.pydantic_models.rename_model import RecordRenamer
from state_voterfiles.utils.db_models.fields.person_name import PersonName
from state_voterfiles.utils.db_models.fields.voter_registration import VoterRegistration
from state_voterfiles.utils.db_models.fields.address import Address, AddressLink
from state_voterfiles.utils.db_models.fields.elections import ElectionTypeDetails, ElectionVoteMethod, ElectionVote, ElectionDataTuple
from state_voterfiles.utils.db_models.fields.phone_number import ValidatedPhoneNumber, PhoneLink
from state_voterfiles.utils.db_models.fields.vendor import VendorTags, VendorName, VendorTagsToVendorLink, VendorTagsToVendorToRecordLink
from state_voterfiles.utils.db_models.fields.vep_keys import VEPMatch
from state_voterfiles.utils.db_models.fields.data_source import DataSource, DataSourceLink
from state_voterfiles.utils.db_models.fields.input_data import InputData
from state_voterfiles.utils.db_models.categories.district_list import FileDistrictList


class CleanUpBaseModel(ValidatorConfig):
    data: RecordRenamer = SQLModelField(...)
    name: Optional[PersonName] = SQLModelField(default=None)
    voter_registration: Optional[VoterRegistration] = SQLModelField(default=None)
    person_details: Dict[str, Any] = SQLModelField(default_factory=dict)
    input_voter_registration: Dict[str, Any] = SQLModelField(default_factory=dict)
    district_set: FileDistrictList = SQLModelField(default_factory=FileDistrictList)

    phone: list[ValidatedPhoneNumber] = SQLModelField(default_factory=list)
    address_list: set['Address'] = SQLModelField(default_factory=set)
    date_format: Any = SQLModelField(default=None)
    settings: Dict[str, Any] = SQLModelField(default=None)
    raw_data: Dict[str, Any] = SQLModelField(default=None)
    vendor_names: set[VendorName] = SQLModelField(default_factory=set)
    vendor_tags: list[VendorTags] = SQLModelField(default_factory=list)
    elections: list[ElectionDataTuple] = SQLModelField(default_factory=list)
    # vote_methods: list[ElectionVoteMethod] = SQLModelField(default_factory=list)
    # vote_history: list[Voted] = SQLModelField(default_factory=list)
    corrected_errors: dict[str, Any] = SQLModelField(default_factory=dict)
    data_source: list[DataSource] = SQLModelField(default_factory=list)
    input_data: Optional[InputData] = SQLModelField(default=None)
    vep_keys: Optional[VEPMatch] = SQLModelField(default=None)
