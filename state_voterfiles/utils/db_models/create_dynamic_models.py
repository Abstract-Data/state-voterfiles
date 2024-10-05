# from __future__ import annotations
# from typing import Optional, List, NamedTuple, Annotated, Type
# from functools import cached_property, wraps
#
# from sqlalchemy.orm import relationship, Mapped, mapped_column
# from sqlalchemy import ForeignKey, Integer, String, Table, Column, UniqueConstraint, and_, text
#
# from pydantic.dataclasses import dataclass as pydantic_dataclass
# from pydantic import Field as PydanticField
# from icecream import ic
#
# from state_voterfiles.utils.db_models.model_bases import Base
# from state_voterfiles.utils.db_models.fields.person_name import PersonNameModel
# from state_voterfiles.utils.db_models.fields.voter_registration import VoterRegistrationModel
# from state_voterfiles.utils.db_models.fields.address import AddressModel
# from state_voterfiles.utils.db_models.fields.phone_number import ValidatedPhoneNumberModel
# from state_voterfiles.utils.db_models.fields.vep_keys import VEPKeysModel
# from state_voterfiles.utils.db_models.fields.district import DistrictModel
# from state_voterfiles.utils.db_models.fields.vendor import VendorTagsModel, VendorNameModel
# from state_voterfiles.utils.db_models.fields.input_data import InputDataModel
# from state_voterfiles.utils.db_models.fields.data_source import DataSourceModel
# from state_voterfiles.utils.db_models.fields.elections import VotedInElectionModel, ElectionTypeModel
# from state_voterfiles.utils.db_models.record import RecordModel
# from state_voterfiles.utils.db_models.fields.record_associations import GenericAssociationModel, AssociationType
#
#
# def class_debugger(cls):
#     class Wrapped(cls):
#         def __init__(self, *args, **kwargs):
#             ic(f"Creating instance of {cls.__name__} with args: {args}, kwargs: {kwargs}")
#             super().__init__(*args, **kwargs)
#
#         def __getattribute__(self, name):
#             attr = super().__getattribute__(name)
#             if callable(attr):
#                 @wraps(attr)
#                 def wrapper(*args, **kwargs):
#                     ic(f"Calling {name} with args: {args}, kwargs: {kwargs}")
#                     return attr(*args, **kwargs)
#                 return wrapper
#             return attr
#
#     return Wrapped
#
#
# def debug_cached_property(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         try:
#             result = func(*args, **kwargs)
#             return result
#         except Exception as e:
#             ic(f'Error in {func.__name__}: {e}')
#             raise
#     return cached_property(wrapper)
#
#
# def mapped_foreign_key(table_name: str):
#     return mapped_column(Integer, ForeignKey(f'{table_name}.id'), nullable=True)
#
#
# @pydantic_dataclass(config={'arbitrary_types_allowed': True})
# class CreateStateModels:
#     record_type: str
#
#     @debug_cached_property
#     def ADDRESS_LIST(self) -> Type[AddressModel]:
#         @class_debugger
#         class DynamicAddress(AddressModel):
#
#             __tablename__ = 'address_list'
#             associations: Mapped[List[GenericAssociationModel]] = relationship(
#                 "GenericAssociationModel",
#                 primaryjoin="and_(GenericAssociationModel.association_type == 'ADDRESS', "
#                             "GenericAssociationModel.associated_id == Address.id)",
#                 back_populates="associated_object"
#             )
#
#         return DynamicAddress
#
#     @debug_cached_property
#     def PHONE_NUMBERS(self) -> Type[ValidatedPhoneNumberModel]:
#         @class_debugger
#         class DynamicPhoneNumber(ValidatedPhoneNumberModel):
#             __tablename__ = 'phone_numbers'
#             associations: Mapped[List[GenericAssociationModel]] = relationship(
#                 "GenericAssociationModel",
#                 primaryjoin="and_(GenericAssociationModel.association_type == 'PHONE', "
#                             "GenericAssociationModel.associated_id == AddressModel.id)",
#                 back_populates="associated_object"
#             )
#
#             @property
#             def associated_records(self):
#                 return [assoc.record for assoc in self.associations]
#
#         return DynamicPhoneNumber
#
#     @debug_cached_property
#     def GOVERNMENT_DISTRICTS(self) -> Type[DistrictModel]:
#         @class_debugger
#         class DynamicDistrictModel(DistrictModel):
#             __tablename__ = 'government_districts'
#             associations: Mapped[List[GenericAssociationModel]] = relationship(
#                 "GenericAssociationModel",
#                 primaryjoin="and_(GenericAssociationModel.association_type == 'DISTRICT', "
#                             "GenericAssociationModel.associated_id == DistrictModel.id)",
#                 back_populates="associated_object"
#             )
#
#         return DynamicDistrictModel
#
#     @debug_cached_property
#     def VENDOR_NAMES(self) -> Type[VendorNameModel]:
#         @class_debugger
#         class DynamicVendorName(VendorNameModel):
#             __tablename__ = 'vendor_name'
#             associations: Mapped[List[GenericAssociationModel]] = relationship(
#                 "GenericAssociationModel",
#                 primaryjoin="and_(GenericAssociationModel.association_type == 'VENDOR', "
#                             "GenericAssociationModel.associated_id == VendorName.id)",
#                 back_populates="associated_object"
#             )
#
#         return DynamicVendorName
#
#     @debug_cached_property
#     def ELECTION_TYPES(self) -> Type[ElectionTypeModel]:
#         @class_debugger
#         class DynamicElectionType(ElectionTypeModel):
#             __tablename__ = 'election_types'
#             associations: Mapped[List[GenericAssociationModel]] = relationship(
#                 "GenericAssociationModel",
#                 primaryjoin="and_(GenericAssociationModel.association_type == 'ELECTION', "
#                             "GenericAssociationModel.associated_id == ElectionTypeModel.id)",
#                 back_populates="associated_object"
#             )
#         return DynamicElectionType
#
#     @debug_cached_property
#     def VOTED_IN_ELECTION(self) -> Type[VotedInElectionModel] | None:
#         if self.record_type == 'voter':
#             @class_debugger
#             class DynamicVotedInElection(VotedInElectionModel):
#                 __tablename__ = f'voted_in_election'
#                 election_id: Mapped[int] = mapped_column(ForeignKey('election_types.id'), nullable=False)
#                 record_id: Mapped[int] = mapped_column(ForeignKey(f'{self.record_type}_record.id'), nullable=False)
#                 election: Mapped[CreateStateModels.ELECTION_TYPES] = relationship(
#                     'DynamicElectionType',
#                     back_populates='voted_in_election',
#                 )
#                 record: Mapped[CreateRecordModels.RECORD] = relationship(
#                     'DynamicRecord',
#                     back_populates='election_history',
#                 )
#             return DynamicVotedInElection
#         return None
#
#     @debug_cached_property
#     def GENERIC_ASSOCIATIONS(self):
#         @class_debugger
#         class DynamicGenericAssociation(GenericAssociationModel):
#             __tablename__ = 'generic_associations'
#             record: Mapped[CreateRecordModels.RECORD] = relationship(
#                 'DynamicRecord',
#                 back_populates='associations',
#             )
#
#         return DynamicGenericAssociation
#
#
#
# @pydantic_dataclass(config={'arbitrary_types_allowed': True})
# class CreateRecordModels:
#     record_type: str
#
#     @debug_cached_property
#     def PERSON_NAME(self) -> Type[PersonNameModel]:
#         @class_debugger
#         class DynamicPersonName(PersonNameModel):
#             __tablename__ = f'{self.record_type}_person_name'
#             record: Mapped[CreateRecordModels.RECORD] = relationship(
#                 'DynamicRecord',
#                 back_populates='name',
#             )
#         return DynamicPersonName
#
#     @debug_cached_property
#     def VOTER_REGISTRATION(self) -> Type[VoterRegistrationModel]:
#         @class_debugger
#         class DynamicVoterRegistration(VoterRegistrationModel):
#             __tablename__ = f'{self.record_type}_voter_registration'
#             record: Mapped[CreateRecordModels.RECORD] = relationship(
#                 'DynamicRecord',
#                 back_populates='voter_registration',
#             )
#         return DynamicVoterRegistration
#
#     @debug_cached_property
#     def VEP_KEYS(self) -> Type[VEPKeysModel]:
#         @class_debugger
#         class DynamicVEPKeys(VEPKeysModel):
#             __tablename__ = f'{self.record_type}_vep_keys'
#             record: Mapped[CreateRecordModels.RECORD] = relationship(
#                 'DynamicRecord',
#                 back_populates='vep_keys',
#             )
#         return DynamicVEPKeys
#
#     @debug_cached_property
#     def INPUT_DATA(self) -> Type[InputDataModel]:
#         @class_debugger
#         class DynamicInputData(InputDataModel):
#             __tablename__ = f'{self.record_type}_input_data'
#             record_id: Mapped[str] = mapped_column(ForeignKey(f'{self.record_type}_record.id'), nullable=False)
#             record: Mapped[CreateRecordModels.RECORD] = relationship(
#                 'DynamicRecord',
#                 back_populates='input_data',
#             )
#         return DynamicInputData
#
#     @debug_cached_property
#     def DATA_SOURCE(self) -> Type[DataSourceModel]:
#         @class_debugger
#         class DynamicDataSource(DataSourceModel):
#             __tablename__ = f'{self.record_type}_data_source'
#             record: Mapped[CreateRecordModels.RECORD] = relationship(
#                 'DynamicRecord',
#                 back_populates='data_sources',
#             )
#         return DynamicDataSource
#
#     @debug_cached_property
#     def RECORD(self) -> Type[RecordModel]:
#         @class_debugger
#         class DynamicRecord(RecordModel):
#             __tablename__ = f'{self.record_type}_record'
#             name_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey(f'{self.record_type}_person_name.id'), nullable=True)
#             voter_registration_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey(f'{self.record_type}_voter_registration.id'), nullable=True)
#             vep_keys_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey(f'{self.record_type}_vep_keys.id'), nullable=True)
#             input_data_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey(f'{self.record_type}_input_data.id'), nullable=True)
#             data_source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey(f'{self.record_type}_data_source.id'), nullable=True)
#
#             name: Mapped[CreateRecordModels.PERSON_NAME] = relationship(
#                 self.PERSON_NAME,
#                 back_populates='record',
#             )
#             voter_registration: Mapped[Optional[CreateRecordModels.VOTER_REGISTRATION]] = relationship(
#                 self.VOTER_REGISTRATION,
#                 back_populates='record',
#             )
#             vep_keys: Mapped[Optional[CreateRecordModels.VEP_KEYS]] = relationship(
#                 self.VEP_KEYS,
#                 back_populates='record',
#             )
#             input_data: Mapped[Optional[CreateRecordModels.INPUT_DATA]] = relationship(
#                 self.INPUT_DATA,
#                 back_populates='record',
#             )
#             data_sources: Mapped[Optional[List[CreateRecordModels.DATA_SOURCE]]] = relationship(
#                 'DynamicDataSource',
#                 back_populates='record',
#             )
#
#             # Generic associations
#             associations: Mapped[List[GenericAssociationModel]] = relationship(
#                 "GenericAssociationModel", back_populates="record", cascade="all, delete-orphan"
#             )
#
#             election_history: Mapped[List[CreateStateModels.VOTED_IN_ELECTION]] = relationship(
#                 "DynamicVotedInElection", back_populates="record", cascade="all, delete-orphan"
#             )
#
#             @property
#             def addresses(self):
#                 return [assoc.associated_object for assoc in self.associations
#                         if assoc.association_type == AssociationType.ADDRESS]
#             @property
#             def phone_numbers(self):
#                 return [assoc.associated_object for assoc in self.associations
#                         if assoc.association_type == AssociationType.PHONE]
#
#             @property
#             def districts(self):
#                 return [assoc.associated_object for assoc in self.associations
#                         if assoc.association_type == AssociationType.DISTRICT]
#
#             @property
#             def vendors(self):
#                 return [assoc.associated_object for assoc in self.associations
#                         if assoc.association_type == AssociationType.VENDOR]
#
#             @property
#             def elections(self):
#                 return [assoc.associated_object for assoc in self.associations
#                         if assoc.association_type == AssociationType.ELECTION]
#
#
#
#
#         return DynamicRecord
#
#
# state_test = CreateStateModels('target')
# record_test = CreateRecordModels('target')
#
# # def create_models(record_type: str):
# #     _type = record_type.lower()
# #
# #     """
# #     ==== General Tables For Each State ====
# #     """
# #     class DynamicAddress(AddressModel):
# #         """ Used as a set for all addresses """
# #         __tablename__ = f'address_list'
# #         record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), nullable=False)
# #         record: Mapped['DynamicRecord'] = relationship(
# #             'DynamicRecord',
# #             back_populates='address_list',
# #             foreign_keys='DynamicAddress.record_id'
# #         )
# #
# #     class DynamicPhoneNumber(ValidatedPhoneNumberModel):
# #         __tablename__ = f'phone_number'
# #         record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), name='record_id')
# #         record: Mapped['DynamicRecord'] = relationship(
# #             'DynamicRecord',
# #             back_populates='phone_numbers',
# #             foreign_keys=[record_id]
# #         )
# #
# #     class DynamicDistrictModel(DistrictModel):
# #         __tablename__ = f'government_districts'
# #         record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), nullable=False)
# #         record: Mapped['DynamicRecord'] = relationship(
# #             'DynamicRecord',
# #             back_populates='districts',
# #             foreign_keys=[record_id]
# #         )
# #
# #     class DynamicVendorName(VendorNameModel):
# #         __tablename__ = f'vendor_name'
# #         record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), nullable=False)
# #         record: Mapped['DynamicRecord'] = relationship(
# #             'DynamicRecord',
# #             back_populates='vendor_name',
# #             foreign_keys=[record_id]
# #         )
# #
# #     class DynamicElectionType(ElectionTypeModel):
# #         __tablename__ = f'election_types'
# #         election_history: Mapped[List['DynamicVotedInElection']] = relationship(
# #             'DynamicVotedInElection',
# #             back_populates='election',
# #         )
#
# """
# ==== Record Type-Specific Tables ====
# """
#
# # class DynamicPersonName(PersonNameModel):
# #     __tablename__ = f'{_type}_person_name'
# #     record: Mapped['DynamicRecord'] = relationship(
# #         'DynamicRecord',
# #         back_populates='name',
# #     )
# #
# # class DynamicVoterRegistration(VoterRegistrationModel):
# #     __tablename__ = f'{_type}_voter_registration'
# #     record: Mapped['DynamicRecord'] = relationship(
# #         'DynamicRecord',
# #         back_populates='voter_registration',
# #     )
# #
# # class DynamicDistrictAssociation(RecordDistrictAssociationModel):
# #     __tablename__ = f'{_type}_district_association'
# #     record_type = _type
# #     district_id: Mapped[int] = mapped_column(ForeignKey('government_districts.id'), nullable=False)
# #     record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), nullable=False)
# #     district: Mapped['DynamicDistrictModel'] = relationship(
# #         'DynamicDistrictModel',
# #         back_populates='record_associations',
# #     )
#
# # class DynamicVEPKeys(VEPKeysModel):
# #     __tablename__ = f'{_type}_vep_keys'
# #     record: Mapped['DynamicRecord'] = relationship(
# #         'DynamicRecord',
# #         back_populates='vep_keys',
# #     )
#
# # class DynamicIndividualDistrict(RecordDistrictModel):
# #     __tablename__ = f'{_type}_government_districts'
# #     record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), nullable=False)
# #     record: Mapped['DynamicRecord'] = relationship(
# #         'DynamicRecord',
# #         back_populates='districts',
# #         foreign_keys=[record_id]
# #     )
#
# # class DynamicVendorTags(VendorTagsModel):
# #     __tablename__ = f'{_type}_vendor_tags'
# #     vendor_id: Mapped[int] = mapped_column(ForeignKey('vendor_name.id'), nullable=False)
# #     record_id: Mapped[int] = mapped_column(Integer, ForeignKey(f'{_type}_record.id'), nullable=False)
# #     vendors: Mapped['DynamicRecord'] = relationship(
# #         'DynamicVendorName',
# #         back_populates='vendor_tags',
# #     )
#
# # class DynamicInputData(InputDataModel):
# #     __tablename__ = f'{_type}_input_data'
# #     record: Mapped['DynamicRecord'] = relationship(
# #         'DynamicRecord',
# #         back_populates='input_data',
# #     )
#
# # class DynamicDataSource(DataSourceModel):
# #     __tablename__ = f'{_type}_data_source'
# #     record: Mapped['DynamicRecord'] = relationship(
# #         'DynamicRecord',
# #         back_populates='data_sources',
# #     )
#
# # if _type == 'voter':
# #     class DynamicVotedInElection(VotedInElectionModel):
# #         __tablename__ = f'{_type}_election_history'
# #         election_id: Mapped[int] = mapped_column(ForeignKey('election_types.id'), nullable=False)
# #         record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), nullable=False)
# #         record_vuid: Mapped[Optional[str]] = mapped_column(ForeignKey('voter_registration.vuid'), nullable=True)
# #         election: Mapped['DynamicElectionType'] = relationship(
# #             'DynamicElectionType',
# #             back_populates='election_history',
# #         )
# #         record: Mapped['DynamicRecord'] = relationship(
# #             'DynamicRecord',
# #             back_populates='election_history',
# #         )
#
# # class DynamicRecord(RecordModel):
# #     __tablename__ = f'{_type}_record'
# #     name_id: Mapped[Optional[int]] = mapped_foreign_key(f'{_type}_person_name')
# #     voter_registration_id: Mapped[Optional[int]] = mapped_foreign_key(f'{_type}_voter_registration')
# #     vep_keys_id: Mapped[Optional[int]] = mapped_foreign_key(f'{_type}_vep_keys')
# #     input_data_id: Mapped[Optional[int]] = mapped_foreign_key(f'{_type}_input_data')
# #     data_source_id: Mapped[Optional[int]] = mapped_foreign_key(f'{_type}_data_source')
# #
# #     name: Mapped['DynamicPersonName'] = relationship(
# #         DynamicPersonName,
# #         back_populates='record',
# #         foreign_keys=[name_id],
# #     )
# #     voter_registration: Mapped[Optional['DynamicVoterRegistration']] = relationship(
# #         DynamicVoterRegistration,
# #         back_populates='record',
# #         foreign_keys=[voter_registration_id],
# #     )
# #     address_list: Mapped[List['DynamicAddress']] = relationship(
# #         'DynamicAddress',
# #         back_populates='record',
# #         foreign_keys=[DynamicAddress.record_id],
# #         cascade="all, delete-orphan"
# #     )
# #     phone_numbers: Mapped[List['DynamicPhoneNumber']] = relationship(
# #         'DynamicPhoneNumber',
# #         back_populates='record',
# #         foreign_keys=[DynamicPhoneNumber.record_id],
# #         cascade="all, delete-orphan"
# #     )
# #     vep_keys: Mapped[Optional['DynamicVEPKeys']] = relationship(
# #         DynamicVEPKeys,
# #         back_populates='record',
# #         foreign_keys=[vep_keys_id],
# #     )
# #     districts: Mapped[List['DynamicIndividualDistrict']] = relationship(
# #         'DynamicIndividualDistrict',
# #         back_populates='record',
# #         foreign_keys=[DynamicIndividualDistrict.record_id],
# #         cascade="all, delete-orphan"
# #     )
# #     vendor_tags: Mapped[Optional[List['DynamicVendorTags']]] = relationship(
# #         'DynamicVendorTags',
# #         back_populates='record',
# #         foreign_keys=[DynamicVendorTags.record_id],
# #         cascade="all, delete-orphan"
# #     )
# #     input_data: Mapped[Optional['DynamicInputData']] = relationship(
# #         DynamicInputData,
# #         back_populates='record',
# #         foreign_keys=[input_data_id],
# #     )
# #     data_sources: Mapped[Optional[List['DynamicDataSource']]] = relationship(
# #         'DynamicDataSource',
# #         back_populates='record',
# #     )
# #     if _type == 'voter':
# #         election_history: Mapped[List['DynamicVotedInElection']] = relationship(
# #             'DynamicElectionHistory',
# #             back_populates='record',
# #             foreign_keys=[DynamicVotedInElection.record_id],
# #             cascade="all, delete-orphan"
# #         )
# #
# # class DynamicRelatedModels(RelatedModels):
# #     RECORD = DynamicRecord
# #     NAME = DynamicPersonName
# #     VOTER_REGISTRATION = DynamicVoterRegistration
# #     ADDRESS = DynamicAddress
# #     PHONE_NUMBER = DynamicPhoneNumber
# #     VEP_KEYS = DynamicVEPKeys
# #     INDIVIDUAL_DISTRICT = DynamicIndividualDistrict
# #     VENDOR_TAGS = DynamicVendorTags
# #     INPUT_DATA = DynamicInputData
# #     DATA_SOURCE = DynamicDataSource
# #     if _type == 'voter':
# #         ELECTION_HISTORY = DynamicVotedInElection
# #
# # return DynamicRelatedModels
