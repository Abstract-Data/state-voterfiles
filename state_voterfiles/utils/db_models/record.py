from __future__ import annotations
from typing import Optional, List, Annotated, Dict, Any, Set

from sqlmodel import Field as SQLModelField, JSON

from .model_bases import ValidatorBaseModel
from .fields.person_name import PersonName
from .fields.voter_registration import VoterRegistration
from .fields.district import District
from .fields.phone_number import ValidatedPhoneNumber
from .fields.vendor import VendorTags, VendorName
from .fields.vep_keys import VEPMatch
from .fields.data_source import DataSource
from .fields.elections import VotedInElection, ElectionTypeDetails
from .fields.input_data import InputData
from .fields.address import Address
from .categories.district_list import FileDistrictList
# from state_voterfiles.utils.db_models.association_validators import GenericAssociation


class RecordBaseModel(ValidatorBaseModel):
    name: PersonName | None = SQLModelField(default=None)
    voter_registration: VoterRegistration | None = SQLModelField(default=None)
    # mailing_id: Annotated[Optional[str], PydanticField(default=None)]
    # residential_id: Annotated[Optional[str], PydanticField(default=None)]
    address_list: set["Address"] = SQLModelField(default_factory=set)
    district_set_id: str | None = SQLModelField(default=None, description='Unique identifier for the district set')
    district_set: FileDistrictList | None = SQLModelField(default=None, description='List of district records')
    phone: list["ValidatedPhoneNumber"] | None = SQLModelField(default_factory=list, sa_type=JSON)
    vendor_names: list["VendorName"] | None = SQLModelField(default_factory=list)
    vendor_tags: list["VendorTags"] | None = SQLModelField(default_factory=list)
    elections: list["ElectionTypeDetails"] | None = SQLModelField(default_factory=list, description='List of election history records')
    vote_history: list["VotedInElection"] | None = SQLModelField(default_factory=list)
    unassigned: Dict[str, Any] | None = SQLModelField(default=None)
    vep_keys: "VEPMatch" = SQLModelField(default_factory=VEPMatch)
    # corrected_errors: Annotated[Dict[str, Any], PydanticField(default_factory=dict)]
    input_data: "InputData" = SQLModelField(default_factory=InputData)
    data_sources: list["DataSource"] = SQLModelField(default_factory=list)

    def create_flat_record(self):
        data = {
            'first_name': self.name.first,
            'last_name': self.name.last,
            'voter_id': self.voter_registration.vuid,
            'dob': self.name.dob,
        }

        for address in self.address_list:
            data[f"{address.address_type}_std"] = address.standardized
            data[f"{address.address_type}_city"] = address.city
            data[f"{address.address_type}_state"] = address.state
            data[f"{address.address_type}_zip"] = address.zip5

        if self.districts:
            for district in self.districts:
                data[f"{district.type}_{district.name}".replace(" ", "_")] = district.county

        if self.phone:
            for phone in self.phone:
                data[f"{phone.phone_type}_PHONE"] = phone.phone

        if self.elections:
            for election in self.elections:
                data[f"{election.year}{election.election_type}_METHOD"] = next((x.vote_method for x in self.vote_history if x.election == election), None)
                data[f"{election.year}{election.election_type}_PARTY"] = next((x.party for x in self.vote_history if x.election == election), None)

        return data


# class RecordModel(Base):
#     __abstract__ = True
#
#     @declared_attr
#     @abc.abstractmethod
#     def name_id(cls) -> Mapped[Optional[int]]:
#         return mapped_column(Integer, ForeignKey(f'{cls.__name__}_person_name.id'), nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def voter_registration_id(cls) -> Mapped[Optional[int]]:
#         return mapped_column(Integer, ForeignKey(f'{cls.__name__}_voter_registration.id'), nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def data_source_id(cls) -> Mapped[int]:
#         return mapped_column(Integer, ForeignKey(f'{cls.__name__}_data_source.id'), nullable=False)
#
#     # @abstract_declared_attr
#     # def address_list_id(cls):
#     #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_address.id'), nullable=True)
#     #
#     # @abstract_declared_attr
#     # def phones_id(cls) -> Mapped[Optional[int]]:
#     #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_validated_phone_number.id'), nullable=True)
#     # @declared_attr
#     # def residential_address_id(cls) -> Mapped[Optional[int]]:
#     #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_residential_address.id'), nullable=True)
#     #
#     # @declared_attr
#     # def mailing_address_id(cls) -> Mapped[Optional[int]]:
#     #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_mailing_address.id'), nullable=True)
#
#     # @declared_attr
#     # def districts_id(cls) -> Mapped[Optional[int]]:
#     #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_government_districts.id'), nullable=True)
#
#     # @declared_attr
#     # def vendors_id(cls) -> Mapped[Optional[int]]:
#     #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_vendor_tags.id'), nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def vep_keys_id(cls) -> Mapped[Optional[int]]:
#         return mapped_column(Integer, ForeignKey(f'{cls.__name__}_vep_keys.id'), nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def input_data_id(cls) -> Mapped[Optional[int]]:
#         return mapped_column(Integer, ForeignKey(f'{cls.__name__}_input_data.id'), nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def name(cls) -> Mapped[Optional['PersonNameModel']]:
#         return relationship(f'{cls.__name__}PersonNameModel', back_populates='record')
#
#     @declared_attr
#     @abc.abstractmethod
#     def voter_registration(cls) -> Mapped[Optional['VoterRegistrationModel']]:
#         return relationship(f'{cls.__name__}VoterRegistrationModel', back_populates='record')
#
#     @declared_attr
#     @abc.abstractmethod
#     def address_list(cls) -> Mapped[Optional[List['AddressModel']]]:
#         return relationship(f'{cls.__name__}AddressModel', back_populates='record')
#
#     @declared_attr
#     @abc.abstractmethod
#     def districts(cls) -> Mapped[Optional['IndividualDistrictModel']]:
#         return relationship(
#             f'{cls.__name__}IndividualDistrictsModel',
#             back_populates='record')
#
#     @declared_attr
#     @abc.abstractmethod
#     def phone_numbers(cls) -> Mapped[List['ValidatedPhoneNumberModel']]:
#         return relationship(f'{cls.__name__}ValidatedPhoneNumberModel')
#
#     @declared_attr
#     @abc.abstractmethod
#     def vendor_tags(cls) -> Mapped[Optional['VendorTagsModel']]:
#         return relationship(f'{cls.__name__}VendorTagsModel', back_populates='record')
#
#     @declared_attr
#     @abc.abstractmethod
#     def vep_keys(cls) -> Mapped[Optional['VEPKeysModel']]:
#         return relationship(f'{cls.__name__}VEPKeysModel', back_populates='record')
#
#     @declared_attr
#     @abc.abstractmethod
#     def input_data(cls) -> Mapped[Optional['InputDataModel']]:
#         return relationship(f'{cls.__name__}InputDataModel', back_populates='record')
#
#     @declared_attr
#     @abc.abstractmethod
#     def data_sources(cls) -> Mapped[List['DataSourceModel']]:
#         return relationship(f'{cls.__name__}DataSourceModel', back_populates='record')
#
#     @classmethod
#     def create_dynamic_model(cls, table_name: str, schema_name: str = None):
#         class DynamicRecord(cls):
#             __tablename__ = table_name
#             __table_args__ = {'schema': schema_name} if schema_name else {}
#
#             if table_name.lower().startswith('voterfile'):
#                 @declared_attr
#                 def election_history(cls) -> Mapped[List['ElectionHistoryModel']]:
#                     return relationship(
#                         f'{cls.__name__}ElectionHistory',
#                         back_populates='record',
#                         cascade="all, delete-orphan"
#                     )
#
#                 @declared_attr
#                 def election_history_id(cls) -> Mapped[Optional[int]]:
#                     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_election_history.id'), nullable=True)
#
#
# class RelatedModels(abc.ABC):
#     RECORD: 'RecordModel'
#     RECORD_VIEW: 'RecordView'
#     NAME: 'PersonNameModel'
#     VOTER_REGISTRATION: 'VoterRegistrationModel'
#     ADDRESS: 'AddressModel'
#     INDIVIDUAL_DISTRICT: 'DistrictModel'
#     RECORD_DISTRICT: 'RecordDistrictModel'
#     PHONE_NUMBER: 'ValidatedPhoneNumberModel'
#     VEP_KEYS: 'VEPKeysModel'
#     VENDOR_TAGS: 'VendorTagsModel'
#     INPUT_DATA: 'InputDataModel'
#     INDIVIDUAL_ELECTION: 'ElectionTypeModel'
