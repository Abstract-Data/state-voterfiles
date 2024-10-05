# from __future__ import annotations
# from typing import Optional, Dict, TypeVar, Any
# from enum import Enum
#
# from sqlalchemy.orm import mapped_column, Mapped, declared_attr, relationship
# from sqlalchemy import Integer, UniqueConstraint, String, ForeignKey, Enum as SQLAEnum, JSON
# from sqlalchemy.ext.associationproxy import association_proxy
# from pydantic import BaseModel, Field, ConfigDict
#
# from state_voterfiles.utils.db_models.fields.address import AddressModel
# from state_voterfiles.utils.db_models.fields.phone_number import ValidatedPhoneNumberModel
# from state_voterfiles.utils.db_models.fields.district import DistrictModel
# from state_voterfiles.utils.db_models.fields.vendor import VendorNameModel
# from state_voterfiles.utils.db_models.fields.elections import VotedInElectionModel, ElectionTypeModel
# from state_voterfiles.utils.db_models.model_bases import Base
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
#     model_config = ConfigDict(arbitrary_types_allowed=True)
#     id: Optional[int] = None
#     association_type: AssociationType
#     associated_id: str  # Using str to match Address.id
#     record_type: str
#     record_id: Optional[str] = None
#     attributes: Dict[str, Any] = Field(default_factory=dict)
#
#
# class GenericAssociationModel(Base):
#     __tablename__ = 'generic_associations'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     association_type: Mapped[AssociationType] = mapped_column(SQLAEnum(AssociationType), nullable=False)
#     associated_id: Mapped[str] = mapped_column(String, nullable=False)
#     record_type: Mapped[str] = mapped_column(String, nullable=False)
#     record_id: Mapped[str] = mapped_column(String, ForeignKey('records.id'), nullable=False)
#     attributes: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
#
#     __table_args__ = (
#         UniqueConstraint('association_type', 'associated_id', 'record_type', 'record_id'),
#     )
#
#     record = relationship("RecordModel", back_populates="associations")
#
#     @property
#     def associated_object(self):
#         if self.association_type == AssociationType.ADDRESS:
#             return AddressModel.query.get(self.associated_id)
#         elif self.association_type == AssociationType.PHONE:
#             return ValidatedPhoneNumberModel.query.get(self.associated_id)
#         elif self.association_type == AssociationType.DISTRICT:
#             return DistrictModel.query.get(self.associated_id)
#         elif self.association_type == AssociationType.VENDOR:
#             return VendorNameModel.query.get(self.associated_id)
#         elif self.association_type == AssociationType.ELECTION:
#             return ElectionTypeModel.query.get(self.associated_id)
#         elif self.association_type == AssociationType.VOTED_IN_ELECTION:
#             return VotedInElectionModel.query.get(self.associated_id)
#         # Add other types as needed
#         return None
