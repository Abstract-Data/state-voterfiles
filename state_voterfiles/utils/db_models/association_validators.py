# from __future__ import annotations
# from pydantic import BaseModel, Field
# from typing import Optional, Dict, TypeVar, Any
# from enum import Enum
#
# from state_voterfiles.utils.db_models.fields.address import Address
# from state_voterfiles.utils.db_models.fields.phone_number import ValidatedPhoneNumber
# from state_voterfiles.utils.db_models.fields.district import District
# from state_voterfiles.utils.db_models.fields.vendor import VendorName
#
# # TODO: Figure out how to make this work with in PreValidationCleanUp Model So I can Get the associations tied together.
#
# T = TypeVar('T')
#
#
# class AssociationType(str, Enum):
#     DISTRICT = "district"
#     PHONE = "phone"
#     ADDRESS = "address"
#     VENDOR = "vendor"
#     ELECTION = "election"
#     VOTED_IN_ELECTION = "voted_in_election"
#
#
# class GenericAssociation(BaseModel):
#     id: Optional[int] = None
#     association_type: AssociationType
#     associated_id: str  # Using str to match Address.id
#     record_type: str
#     record_id: Optional[str] = None
#     attributes: Dict[str, Any] = Field(default_factory=dict)