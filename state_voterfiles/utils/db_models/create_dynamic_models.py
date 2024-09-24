from typing import Optional, List
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer

from state_voterfiles.utils.db_models.fields.person_name import PersonNameModel
from state_voterfiles.utils.db_models.fields.voter_registration import VoterRegistrationModel
from state_voterfiles.utils.db_models.fields.address import AddressModel
from state_voterfiles.utils.db_models.fields.phone_number import ValidatedPhoneNumberModel
from state_voterfiles.utils.db_models.fields.vep_keys import VEPKeysModel
from state_voterfiles.utils.db_models.fields.district import RecordDistrictModel
from state_voterfiles.utils.db_models.fields.vendor import VendorTagsModel
from state_voterfiles.utils.db_models.fields.input_data import InputDataModel
from state_voterfiles.utils.db_models.fields.data_source import DataSourceModel
from state_voterfiles.utils.db_models.fields.elections import VotedInElectionModel
from state_voterfiles.utils.db_models.fields.record import RecordModel, RelatedModels


def mapped_foreign_key(table_name: str):
    return mapped_column(Integer, ForeignKey(f'{table_name}.id'), nullable=True)


def create_models(record_type: str):
    _type = record_type.lower()

    class DynamicPersonName(PersonNameModel):
        __tablename__ = f'{_type}_person_name'
        record: Mapped['DynamicRecord'] = relationship(
            'DynamicRecord',
            back_populates='name',
        )

    class DynamicVoterRegistration(VoterRegistrationModel):
        __tablename__ = f'{_type}_voter_registration'
        record: Mapped['DynamicRecord'] = relationship(
            'DynamicRecord',
            back_populates='voter_registration',
        )

    class DynamicAddress(AddressModel):
        __tablename__ = f'{_type}_address_list'
        record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), nullable=False)
        record: Mapped['DynamicRecord'] = relationship(
            'DynamicRecord',
            back_populates='address_list',
            foreign_keys='DynamicAddress.record_id'
        )

    class DynamicPhoneNumber(ValidatedPhoneNumberModel):
        __tablename__ = f'{_type}_phone_number'
        record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), name='record_id')
        record: Mapped['DynamicRecord'] = relationship(
            'DynamicRecord',
            back_populates='phone_numbers',
            foreign_keys=[record_id]
        )

    class DynamicVEPKeys(VEPKeysModel):
        __tablename__ = f'{_type}_vep_keys'
        record: Mapped['DynamicRecord'] = relationship(
            'DynamicRecord',
            back_populates='vep_keys',
        )

    class DynamicIndividualDistrict(RecordDistrictModel):
        __tablename__ = f'{_type}_government_districts'
        record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), nullable=False)
        record: Mapped['DynamicRecord'] = relationship(
            'DynamicRecord',
            back_populates='districts',
            foreign_keys=[record_id]
        )

    class DynamicVendorTags(VendorTagsModel):
        __tablename__ = f'{_type}_vendor_tags'
        record_id: Mapped[int] = mapped_column(Integer, ForeignKey(f'{_type}_record.id'), nullable=False)
        record: Mapped['DynamicRecord'] = relationship(
            'DynamicRecord',
            back_populates='vendor_tags',
            foreign_keys=[record_id]
        )

    class DynamicInputData(InputDataModel):
        __tablename__ = f'{_type}_input_data'
        record: Mapped['DynamicRecord'] = relationship(
            'DynamicRecord',
            back_populates='input_data',
        )

    class DynamicDataSource(DataSourceModel):
        __tablename__ = f'{_type}_data_source'
        record: Mapped['DynamicRecord'] = relationship(
            'DynamicRecord',
            back_populates='data_sources',
        )

    if _type == 'voter':
        class DynamicVotedInElection(VotedInElectionModel):
            __tablename__ = f'{_type}_election_history'
            record_id: Mapped[int] = mapped_column(ForeignKey(f'{_type}_record.id'), nullable=False)
            record_vuid: Mapped[str] = mapped_column(ForeignKey(f'{_type}_voter_registration.vuid'), nullable=False)
            record: Mapped['DynamicRecord'] = relationship(
                'DynamicRecord',
                back_populates='election_history',
                foreign_keys=[record_id]
            )

    class DynamicRecord(RecordModel):
        __tablename__ = f'{_type}_record'
        name_id: Mapped[Optional[int]] = mapped_foreign_key(f'{_type}_person_name')
        voter_registration_id: Mapped[Optional[int]] = mapped_foreign_key(f'{_type}_voter_registration')
        vep_keys_id: Mapped[Optional[int]] = mapped_foreign_key(f'{_type}_vep_keys')
        input_data_id: Mapped[Optional[int]] = mapped_foreign_key(f'{_type}_input_data')
        data_source_id: Mapped[Optional[int]] = mapped_foreign_key(f'{_type}_data_source')

        name: Mapped['DynamicPersonName'] = relationship(
            DynamicPersonName,
            back_populates='record',
            foreign_keys=[name_id],
        )
        voter_registration: Mapped[Optional['DynamicVoterRegistration']] = relationship(
            DynamicVoterRegistration,
            back_populates='record',
            foreign_keys=[voter_registration_id],
        )
        address_list: Mapped[List['DynamicAddress']] = relationship(
            'DynamicAddress',
            back_populates='record',
            foreign_keys=[DynamicAddress.record_id],
            cascade="all, delete-orphan"
        )
        phone_numbers: Mapped[List['DynamicPhoneNumber']] = relationship(
            'DynamicPhoneNumber',
            back_populates='record',
            foreign_keys=[DynamicPhoneNumber.record_id],
            cascade="all, delete-orphan"
        )
        vep_keys: Mapped[Optional['DynamicVEPKeys']] = relationship(
            DynamicVEPKeys,
            back_populates='record',
            foreign_keys=[vep_keys_id],
        )
        districts: Mapped[List['DynamicIndividualDistrict']] = relationship(
            'DynamicIndividualDistrict',
            back_populates='record',
            foreign_keys=[DynamicIndividualDistrict.record_id],
            cascade="all, delete-orphan"
        )
        vendor_tags: Mapped[Optional[List['DynamicVendorTags']]] = relationship(
            'DynamicVendorTags',
            back_populates='record',
            foreign_keys=[DynamicVendorTags.record_id],
            cascade="all, delete-orphan"
        )
        input_data: Mapped[Optional['DynamicInputData']] = relationship(
            DynamicInputData,
            back_populates='record',
            foreign_keys=[input_data_id],
        )
        data_sources: Mapped[Optional[List['DynamicDataSource']]] = relationship(
            'DynamicDataSource',
            back_populates='record',
        )
        if _type == 'voter':
            election_history: Mapped[List['DynamicVotedInElection']] = relationship(
                'DynamicElectionHistory',
                back_populates='record',
                foreign_keys=[DynamicVotedInElection.record_id],
                cascade="all, delete-orphan"
            )

    class DynamicRelatedModels(RelatedModels):
        RECORD = DynamicRecord
        NAME = DynamicPersonName
        VOTER_REGISTRATION = DynamicVoterRegistration
        ADDRESS = DynamicAddress
        PHONE_NUMBER = DynamicPhoneNumber
        VEP_KEYS = DynamicVEPKeys
        INDIVIDUAL_DISTRICT = DynamicIndividualDistrict
        VENDOR_TAGS = DynamicVendorTags
        INPUT_DATA = DynamicInputData
        DATA_SOURCE = DynamicDataSource
        if _type == 'voter':
            ELECTION_HISTORY = DynamicVotedInElection

    return DynamicRelatedModels
