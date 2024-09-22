from __future__ import annotations
from ..base import Base, mapped_column, Mapped
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship, declared_attr
import abc


class RecordModel(Base):
    __abstract__ = True

    @declared_attr
    @abc.abstractmethod
    def name_id(cls) -> Mapped[Optional[int]]:
        return mapped_column(Integer, ForeignKey(f'{cls.__name__}_person_name.id'), nullable=True)

    @declared_attr
    @abc.abstractmethod
    def voter_registration_id(cls) -> Mapped[Optional[int]]:
        return mapped_column(Integer, ForeignKey(f'{cls.__name__}_voter_registration.id'), nullable=True)

    @declared_attr
    @abc.abstractmethod
    def data_source_id(cls) -> Mapped[int]:
        return mapped_column(Integer, ForeignKey(f'{cls.__name__}_data_source.id'), nullable=False)

    # @abstract_declared_attr
    # def address_list_id(cls):
    #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_address.id'), nullable=True)
    #
    # @abstract_declared_attr
    # def phones_id(cls) -> Mapped[Optional[int]]:
    #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_validated_phone_number.id'), nullable=True)
    # @declared_attr
    # def residential_address_id(cls) -> Mapped[Optional[int]]:
    #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_residential_address.id'), nullable=True)
    #
    # @declared_attr
    # def mailing_address_id(cls) -> Mapped[Optional[int]]:
    #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_mailing_address.id'), nullable=True)

    # @declared_attr
    # def districts_id(cls) -> Mapped[Optional[int]]:
    #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_government_districts.id'), nullable=True)

    # @declared_attr
    # def vendors_id(cls) -> Mapped[Optional[int]]:
    #     return mapped_column(Integer, ForeignKey(f'{cls.__name__}_vendor_tags.id'), nullable=True)

    @declared_attr
    def vep_keys_id(cls) -> Mapped[Optional[int]]:
        return mapped_column(Integer, ForeignKey(f'{cls.__name__}_vep_keys.id'), nullable=True)

    @declared_attr
    def input_data_id(cls) -> Mapped[Optional[int]]:
        return mapped_column(Integer, ForeignKey(f'{cls.__name__}_input_data.id'), nullable=True)

    @declared_attr
    def name(cls) -> Mapped[Optional['PersonNameModel']]:
        return relationship(f'{cls.__name__}PersonNameModel', back_populates='record')

    @declared_attr
    def voter_registration(cls) -> Mapped[Optional['VoterRegistrationModel']]:
        return relationship(f'{cls.__name__}VoterRegistrationModel', back_populates='record')

    @declared_attr
    def address_list(cls) -> Mapped[Optional[List['AddressModel']]]:
        return relationship(f'{cls.__name__}AddressModel', back_populates='record')

    @declared_attr
    def districts(cls) -> Mapped[Optional['IndividualDistrictModel']]:
        return relationship(
            f'{cls.__name__}IndividualDistrictsModel',
            back_populates='record')

    @declared_attr
    def phone_numbers(cls) -> Mapped[List['ValidatedPhoneNumberModel']]:
        return relationship(f'{cls.__name__}ValidatedPhoneNumberModel')

    @declared_attr
    def vendor_tags(cls) -> Mapped[Optional['VendorTagsModel']]:
        return relationship(f'{cls.__name__}VendorTagsModel', back_populates='record')

    @declared_attr
    def vep_keys(cls) -> Mapped[Optional['VEPKeysModel']]:
        return relationship(f'{cls.__name__}VEPKeysModel', back_populates='record')

    @declared_attr
    def input_data(cls) -> Mapped[Optional['InputDataModel']]:
        return relationship(f'{cls.__name__}InputDataModel', back_populates='record')

    @declared_attr
    def data_sources(cls) -> Mapped[List['DataSourceModel']]:
        return relationship(f'{cls.__name__}DataSourceModel', back_populates='record')

    @classmethod
    def create_dynamic_model(cls, table_name: str, schema_name: str = None):
        class DynamicRecord(cls):
            __tablename__ = table_name
            __table_args__ = {'schema': schema_name} if schema_name else {}

            if table_name.lower().startswith('voterfile'):
                @declared_attr
                def election_history(cls) -> Mapped[List['ElectionHistoryModel']]:
                    return relationship(
                        f'{cls.__name__}ElectionHistory',
                        back_populates='record',
                        cascade="all, delete-orphan"
                    )

                @declared_attr
                def election_history_id(cls) -> Mapped[Optional[int]]:
                    return mapped_column(Integer, ForeignKey(f'{cls.__name__}_election_history.id'), nullable=True)


class RelatedModels(abc.ABC):
    RECORD: 'RecordModel'
    RECORD_VIEW: 'RecordView'
    NAME: 'PersonNameModel'
    VOTER_REGISTRATION: 'VoterRegistrationModel'
    ADDRESS: 'AddressModel'
    INDIVIDUAL_DISTRICT: 'DistrictModel'
    RECORD_DISTRICT: 'RecordDistrictModel'
    PHONE_NUMBER: 'ValidatedPhoneNumberModel'
    VEP_KEYS: 'VEPKeysModel'
    VENDOR_TAGS: 'VendorTagsModel'
    INPUT_DATA: 'InputDataModel'
    INDIVIDUAL_ELECTION: 'ElectionTypeModel'
