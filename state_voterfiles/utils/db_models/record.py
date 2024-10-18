import datetime
from typing import Dict, Any
from enum import StrEnum

from sqlmodel import Field as SQLModelField, JSON, Relationship, SQLModel, Session, select, Relationship, ForeignKey
from sqlalchemy.orm import configure_mappers, declared_attr
from sqlalchemy import Engine, event, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from pydantic import model_validator

from state_voterfiles.utils.db_models.fields.person_name import PersonName
from state_voterfiles.utils.db_models.fields.voter_registration import VoterRegistration
from state_voterfiles.utils.db_models.fields.address import Address, AddressLink
from state_voterfiles.utils.db_models.fields.elections import (
    ElectionTypeDetails, ElectionVote, ElectionVoteMethod)
# from ..db_models.fields.district import District
from state_voterfiles.utils.db_models.fields.phone_number import ValidatedPhoneNumber, PhoneLink
from state_voterfiles.utils.db_models.fields.vendor import (
    VendorTags,
    VendorName,
    VendorTagsToVendorLink,
    VendorTagsToVendorToRecordLink
)
from state_voterfiles.utils.db_models.fields.vep_keys import VEPMatch
from state_voterfiles.utils.db_models.fields.data_source import DataSource, DataSourceLink
from state_voterfiles.utils.db_models.fields.input_data import InputData
from state_voterfiles.utils.db_models.fields.district import District, FileDistrictList, DistrictSetLink
# from ..db_models.categories.district_list import FileDistrictList


# TODO: Consider storing the PreValidationCleanup as a PrivateAttr on the model so it can be referenced
#  to create the relationship model. This will allow for the model to be created dynamically.

# TODO: Make sure there are not SETS in the Validated RecordBaseModel or else it will throw an error.
#  Sets must be a list.

# TODO: Attempt to put back relationships in each model respectively, using forward refs where appropriate.
#  Use 'ForwardRefs' for RecordBaseModel.

MODEL_LIST = [Address, PersonName, VoterRegistration, ValidatedPhoneNumber, VendorName, VendorTags, ElectionTypeDetails,
              ElectionVoteMethod, ElectionVote, DataSource, InputData, VEPMatch,  District,]
class RecordBaseModel(SQLModel, table=True):
    id: int | None = SQLModelField(
        default=None,
        primary_key=True)
    name_id: str | None = SQLModelField(
        default=None,
        foreign_key=f'{PersonName.__tablename__}.id')
    voter_registration_id: str | None = SQLModelField(
        default=None,
        foreign_key=f'{VoterRegistration.__tablename__}.vuid',
        unique=True)
    # vote_history_id: str | None = SQLModelField(
    #     default=None,
    #     foreign_key=f'{VotedInElection.__tablename__}.voter_id')
    district_set_id: str | None = SQLModelField(default=None, foreign_key="filedistrictlist.id")
    vep_keys_id: int | None = SQLModelField(
        default=None,
        foreign_key=f'{VEPMatch.__tablename__}.id')
    input_data_id: int | None = SQLModelField(
        default=None,
        foreign_key=f'{InputData.__tablename__}.id')
    name: "PersonName" = Relationship(
        back_populates='records')
    voter_registration: "VoterRegistration" = Relationship(
        back_populates='records')
    address_list: list["Address"] = Relationship(
        back_populates='records',
        link_model=AddressLink)
    # district_links: list["DistrictLink"] = Relationship(
    #     back_populates="record")
    district_set: "FileDistrictList" = Relationship(back_populates="record_set")
    phone_numbers: list["ValidatedPhoneNumber"] = Relationship(
        back_populates='records',
        link_model=PhoneLink)
    vendor_tag_record_links: list["VendorTagsToVendorToRecordLink"] = Relationship(
        back_populates='record')
    vote_history: list[ElectionVote] = Relationship(
        back_populates="record",
        # link_model=ElectionAndVoterLink,
        # sa_relationship_kwargs={
        #     'primaryjoin': 'RecordBaseModel.voter_registration_id == ElectionAndVoterLink.record_voter_id',
        #     'secondaryjoin': 'ElectionAndVoterLink.election_vote_id == ElectionVote.id'
        # }
    )
        # sa_relationship_kwargs={
        #     'primaryjoin': 'RecordBaseModel.voter_registration_id == VoterAndElectionLink.voter_id',
        #     'secondaryjoin': 'VoterAndElectionLink.vote_history_id == VotedInElection.id',
        #     'overlaps': "voters,vote_history"
        # }
    # vote_history: list["VotedInElection"] = SQLModelField(default_factory=list)
    # unassigned: dict[str, Any] = SQLModelField(
    #     default=None,
    #     sa_type=JSON)
    vep_keys: "VEPMatch" = Relationship(
        back_populates='records')
    input_data: "InputData" = Relationship(
        back_populates='records')
    data_source: list["DataSource"] = Relationship(
        back_populates='records',
        link_model=DataSourceLink)

    # def __init__(self):
    #     super().__init__()
    #     AddressLink.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f'f{RecordBaseModel.__tablename__}.id',
    #         primary_key=True)
    #
    #     PhoneLink.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f'{RecordBaseModel.__tablename__}.id',
    #         primary_key=True)
    #
    #     # # Relationships from elections.py
    #     ElectionLinkToRecord.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f'{RecordBaseModel.__tablename__}.id',
    #         primary_key=True)
    #     ElectionLinkToRecord.record = Relationship(back_populates="election_link_records")
    #
    #     # Relationships from data_source.py
    #     DataSourceLink.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f'{RecordBaseModel.__tablename__}.id',
    #         primary_key=True)
    #
    #     # Relationships from district.py
    #     DistrictLink.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f"{RecordBaseModel.__tablename__}.id",
    #         primary_key=True)
    #     DistrictLinkToRecord.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f"{RecordBaseModel.__tablename__}.id",
    #         primary_key=True)
    #     DistrictLinkToRecord.record = Relationship(back_populates="district_link_records")
    #     configure_mappers()

    @staticmethod
    def add_created_and_updated_columns():
        for model in MODEL_LIST:
            model.add_created_and_update_columns()


    @staticmethod
    def set_relationships(data: "PreValidationCleanUp", engine: Engine):
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            session.add(data.name)
            session.add(data.voter_registration)
            session.add(data.vep_keys)
            session.add(data.input_data)
            session.commit()

            _final = RecordBaseModel(
                name=data.name,
                voter_registration_id=data.voter_registration.id,
                voter_registration=data.voter_registration,
                vep_keys=data.vep_keys,
                input_data=data.input_data
            )
            session.add(_final)
            for address in data.address_list:
                try:
                    session.add(address)
                    session.commit()
                except IntegrityError as e:
                    session.rollback()
                    session.merge(address)
                _final.address_list.append(address)

            if data.data_source:
                existing_data_source = session.execute(
                    select(DataSource).where(DataSource.file == data.data_source.file)
                ).scalar_one_or_none()

                if existing_data_source:
                    data.data_source = existing_data_source
                else:
                    session.add(data.data_source)
                _final.data_source.append(data.data_source)

            _phone_numbers = [data.phone] if data.phone else []
            session.add_all(_phone_numbers)
            session.commit()

            # Merge elections
            if data.elections:
                current_time = datetime.datetime.now()
                for election in data.elections:
                    _election = election.election
                    _vote_method = election.vote_method
                    _vote_record = election.vote_record
                    for each in [_election, _vote_method]:
                        try:
                            session.add(each)
                            session.commit()
                        except IntegrityError as e:
                            session.rollback()
                            session.merge(each)

                    _election.election_vote_methods.append(_vote_method)
                    _vote_record.voter_id = _final.voter_registration_id
                    _final.vote_history.append(_vote_record)

            try:
                session.commit()
            except IntegrityError as e:
                session.rollback()
                print(f"IntegrityError occurred: {e}")

            if data.district_set:
                try:
                    session.add(data.district_set)
                    session.commit()
                except IntegrityError as e:
                    session.rollback()
                    session.merge(data.district_set)
                _final.district_set_id = data.district_set.id

            _vendor_names_link = [
                VendorTagsToVendorLink(
                    vendor_id=x.id,
                    tag_id=_final.id
                ) for x in data.vendor_names
            ] if data.vendor_names else []

            _vendor_tags_link = [
                VendorTagsToVendorLink(
                    vendor_id=x.id,
                    tag_id=_final.id
                ) for x in data.vendor_tags
            ] if data.vendor_tags else []
            session.add_all(_vendor_names_link)
            session.add_all(_vendor_tags_link)
            session.commit()

    # def create_flat_record(self):
    #     data = {
    #         'first_name': self.name.first,
    #         'last_name': self.name.last,
    #         'voter_id': self.voter_registration.vuid,
    #         'dob': self.name.dob,
    #     }
    #
    #     for address in self.address_list:
    #         data[f"{address.address_type}_std"] = address.standardized
    #         data[f"{address.address_type}_city"] = address.city
    #         data[f"{address.address_type}_state"] = address.state
    #         data[f"{address.address_type}_zip"] = address.zip5
    #
    #     if self.districts:
    #         for district in self.districts:
    #             data[f"{district.type}_{district.name}".replace(" ", "_")] = district.county
    #
    #     if self.phone:
    #         for phone in self.phone:
    #             data[f"{phone.phone_type}_PHONE"] = phone.phone
    #
    #     if self.elections:
    #         for election in self.elections:
    #             data[f"{election.year}{election.election_type}_METHOD"] = next(
    #                 (x.vote_method for x in self.vote_history if x.election == election), None)
    #             data[f"{election.year}{election.election_type}_PARTY"] = next(
    #                 (x.party for x in self.vote_history if x.election == election), None)
    #
    #     return data


# class RecordBaseModel(_model_bases.ValidatorBaseModel, table=True):
#     name: PersonName | None = SQLModelField(default=None)
#     voter_registration: VoterRegistration | None = SQLModelField(default=None)
#     # mailing_id: Annotated[Optional[str], PydanticField(default=None)]
#     # residential_id: Annotated[Optional[str], PydanticField(default=None)]
#     address_list: set['Address'] = SQLModelField(default_factory=set)
#     district_set: FileDistrictList | None = SQLModelField(default=None, description='List of district records')
#     phone: list["ValidatedPhoneNumber"] | None = SQLModelField(default_factory=list)
#     vendor_names: set[VendorName] | None = SQLModelField(default_factory=set)
#     vendor_tags: list["VendorTags"] | None = SQLModelField(default_factory=list)
#     elections: list["ElectionTypeDetails"] | None = SQLModelField(default_factory=list,
#                                                                   description='List of election history records')
#     vote_history: list["VotedInElection"] | None = SQLModelField(default_factory=list)
#     unassigned: Dict[str, Any] | None = SQLModelField(default=None)
#     vep_keys: VEPMatch = SQLModelField(default_factory=VEPMatch)
#     # corrected_errors: Annotated[Dict[str, Any], PydanticField(default_factory=dict)]
#     input_data: InputData = SQLModelField(default_factory=InputData)
#     data_source: DataSource = SQLModelField(default_factory=DataSource)
#     db_model: SQLModel | None = None
#
#     def __init__(self, **data):
#         super().__init__(**data)
#         RecordBaseModel.__tablename__ = self.input_data.settings.get('FILE-TYPE')
#
#
#     def create_flat_record(self):
#         data = {
#             'first_name': self.name.first,
#             'last_name': self.name.last,
#             'voter_id': self.voter_registration.vuid,
#             'dob': self.name.dob,
#         }
#
#         for address in self.address_list:
#             data[f"{address.address_type}_std"] = address.standardized
#             data[f"{address.address_type}_city"] = address.city
#             data[f"{address.address_type}_state"] = address.state
#             data[f"{address.address_type}_zip"] = address.zip5
#
#         if self.districts:
#             for district in self.districts:
#                 data[f"{district.type}_{district.name}".replace(" ", "_")] = district.county
#
#         if self.phone:
#             for phone in self.phone:
#                 data[f"{phone.phone_type}_PHONE"] = phone.phone
#
#         if self.elections:
#             for election in self.elections:
#                 data[f"{election.year}{election.election_type}_METHOD"] = next(
#                     (x.vote_method for x in self.vote_history if x.election == election), None)
#                 data[f"{election.year}{election.election_type}_PARTY"] = next(
#                     (x.party for x in self.vote_history if x.election == election), None)
#
#         return data
        # session.merge(tables.voter_registration(**self.voter_registration.model_dump()))
        # session.merge(self.input_data)
        # if session.exec(select(DataSource).where(DataSource.file == self.data_source.file)).first():
        #     session.merge(self.data_source)
        # else:
        #     session.add(self.data_source)
        #     session.commit()
        #     session.refresh(self.data_source)
        #
        # _model = self.db_model(
        #     name_id=self.name.id,
        #     voter_registration_id=self.voter_registration.id,
        #     vep_keys_id=self.vep_keys.id,
        #     input_data_id=self.input_data.id
        # )
        # session.add(_model)
        #
        # session.add(DataSourceLink(data_source_id=self.data_source.id, record_id=_model.id))
        # session.add(_model)
        # session.commit()
        # session.refresh(_model)
        #
        #
        # for address in self.address_list:
        #     session.merge(address)
        #     session.add(
        #         RecordAddressLink(
        #             address_id=address.id,
        #             record_id=_model.id,
        #             is_mailing=address.is_mailing,
        #             is_residence=address.is_residence
        #         )
        #     )
        #
        # if self.district_set:
        #     for district in self.district_set.districts:
        #         session.add(district)
        #         session.add(RecordDistrictLink(district_id=district.id, record_id=_model.id))
        #
        # if self.phone:
        #     for phone in self.phone:
        #         session.add(phone)
        #         session.add(RecordPhoneLink(phone_id=phone.id, record_id=_model.id))
        #
        # if self.vote_history:
        #     session.add_all([x for x in self.elections])
        #     for vote in self.vote_history:
        #         session.add(vote)
        #         session.add(
        #             RecordElectionLink(
        #                 election_id=vote.election_id,
        #                 vote_details_id=vote.id,
        #                 record_id=_model.id
        #             )
        #         )
        #
        # if self.vendor_names:
        #     for vendor in self.vendor_names:
        #         session.add(vendor)
        #         session.refresh(vendor)
        #
        # if self.vendor_tags:
        #     for tag in self.vendor_tags:
        #         session.add(tag)
        #         session.add(VendorNameToTagLink(vendor_id=vendor.id, tag_id=tag.id))
        #         session.add(RecordVendorTagLink(tag_id=tag.id, record_id=_model.id))
        # session.commit()
        # return _model

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
