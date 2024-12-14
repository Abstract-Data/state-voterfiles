from dataclasses import dataclass, field
from typing import Optional, Annotated, Dict, Any, Set, Type, ForwardRef
from enum import Enum
from copy import deepcopy

from sqlmodel import Field as SQLModelField, JSON, Relationship, SQLModel, Session, select
from sqlalchemy.orm import configure_mappers, joinedload
from sqlalchemy.engine import Engine


from election_utils.election_models import VotedInElection, ElectionTypeDetails

from vep_validation_tools.pydantic_models.model_bases import ValidatorBaseModel
from vep_validation_tools.pydantic_models.fields.person_name import PersonName
from vep_validation_tools.pydantic_models.fields.voter_registration import VoterRegistration
from vep_validation_tools.pydantic_models.fields.district import District
from vep_validation_tools.pydantic_models.fields.phone_number import ValidatedPhoneNumber
from vep_validation_tools.pydantic_models.fields.vendor import VendorTags, VendorName
from vep_validation_tools.pydantic_models.fields.vep_keys import VEPMatch
from vep_validation_tools.pydantic_models.fields.data_source import DataSource
from vep_validation_tools.pydantic_models.fields.input_data import InputData
from vep_validation_tools.pydantic_models.fields.address import Address
from vep_validation_tools.pydantic_models.record import RecordBaseModel
from vep_validation_tools.pydantic_models.categories.district_list import FileDistrictList
from .pydantic_models.x_categories.x_address_list import FileAddressList
from .pydantic_models.x_categories.vendor_list import FileVendorNameList


class TableEnum(Enum):
    RECORD_PERSON_NAME = 'RecordPersonName'
    RECORD_ADDRESS_LINK = 'RecordAddressLink'
    RECORD_PHONE_LINK = 'RecordPhoneLink'
    RECORD_DISTRICT_LINK = 'RecordDistrictLink'
    RECORD_ELECTION_LINK = 'RecordElectionLink'
    RECORD_DATA_SOURCE_LINK = 'RecordDataSourceLink'
    RECORD_VENDOR_NAME_TO_TAG_LINK = 'RecordVendorNameToTagLink'
    RECORD_VENDOR_TAGS = 'RecordVendorTags'
    RECORD_VENDOR_NAME = 'RecordVendorName'
    RECORD_VOTER_REGISTRATION = 'RecordVoterRegistration'
    RECORD_ADDRESS = 'RecordAddress'
    RECORD_VALIDATED_PHONE_NUMBER = 'RecordValidatedPhoneNumber'
    RECORD_ELECTION_TYPE_DETAILS = 'RecordElectionTypeDetails'
    RECORD_VOTED_IN_ELECTION = 'RecordVotedInElection'
    RECORD_VEP_MATCH = 'RecordVEPMatch'
    RECORD_DATA_SOURCE = 'RecordDataSource'
    RECORD_INPUT_DATA = 'RecordInputData'
    RECORD_DISTRICT = 'RecordDistrict'
    DATA_BASE_MODEL = 'DataBaseModel'

    def __call__(self):
        return deepcopy(self.value)


@dataclass
class CreateDatabaseTables:
    validator: SQLModel
    engine: Engine
    record_type: str = None
    tables: Dict[str, Type[SQLModel]] = field(default_factory=dict)

    # record: Type[ForwardRef('DataBaseModel')] = None
    # person_name: Type[ForwardRef('RecordPersonName')] = None
    # address: Type[ForwardRef('RecordAddress')] = None
    # address_link: Type[ForwardRef('RecordAddressLink')] = None
    # phone: Type[ForwardRef('RecordValidatedPhoneNumber')] = None
    # phone_link: Type[ForwardRef('RecordPhoneLink')] = None
    # district: Type[ForwardRef('RecordDistrict')] = None
    # district_link: Type[ForwardRef('RecordDistrictLink')] = None
    # election_link: Type[ForwardRef('RecordElectionLink')] = None
    # vendor_name: Type[ForwardRef('RecordVendorName')] = None
    # vendor_tags: Type[ForwardRef('RecordVendorTags')] = None
    # data_source: Type[ForwardRef('RecordDataSource')] = None
    # data_source_link: Type[ForwardRef('RecordDataSourceLink')] = None
    # vendor_name_to_tag_link: Type[ForwardRef('RecordVendorNameToTagLink')] = None
    # voter_registration: Type[ForwardRef('RecordVoterRegistration')] = None
    # input_data: Type[ForwardRef('RecordInputData')] = None
    # election_type: Type[ForwardRef('RecordElectionTypeDetails')] = None
    # vote_history: Type[ForwardRef('RecordVotedInElection')] = None
    # vep_keys: Type[ForwardRef('RecordVEPMatch')] = None

    def __post_init__(self):
        self.check_record_type()

    def check_record_type(self):
        match val_name := self.validator.__name__.lower():
            case _ if 'voterfile' in val_name:
                self.record_type = 'voterfile'
            case _ if 'target' in val_name:
                self.record_type = 'target'
        return self.record_type

    def create_tables(self):

        # class RecordPersonName(PersonName, table=True):
        #     __tablename__ = f'{self.record_type}_person_name'
        #     records: 'DataBaseModel' = Relationship(back_populates='name')

        # class RecordAddressLink(SQLModel, table=True):
        #     __tablename__ = f'{self.record_type}_address_link'
        #     address_id: Optional[str] = SQLModelField(
        #         default=None,
        #         foreign_key=f"{self.record_type}_{Address.__tablename__}.id",
        #         primary_key=True)
        #     record_id: int | None = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.validator.__tablename__}.id',
        #         primary_key=True)

        # class RecordPhoneLink(SQLModel, table=True):
        #     __tablename__ = f'{self.record_type}_phone_link'
        #     phone_id: Optional[str] = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.record_type}_{ValidatedPhoneNumber.__tablename__}.id',
        #         primary_key=True)
        #     record_id: Optional[int] = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.validator.__tablename__}.id',
        #         primary_key=True)

        # class RecordDistrictLink(SQLModel, table=True):
        #     __tablename__ = f'{self.record_type}_districts_link'
        #     district_id: Optional[str] = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.record_type}_{District.__tablename__}.id',
        #         primary_key=True)
        #     record_id: int | None = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.validator.__tablename__}.id',
        #         primary_key=True)
        #     records: 'DataBaseModel' = Relationship(back_populates='district_links')
        #     district: 'RecordDistrict' = Relationship(back_populates='record_links')

        # class RecordElectionLink(ValidatorBaseModel, table=True):
        #     __tablename__ = f'{self.record_type}_election_link'
        #     election_id: str | None = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.record_type}_{ElectionTypeDetails.__tablename__}.id',
        #         primary_key=True)
        #     vote_details_id: str | None = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.record_type}_{VotedInElection.__tablename__}.id',
        #         primary_key=True)
        #     record_id: int | None = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.validator.__tablename__}.id',
        #         primary_key=True)
        #
        #     record: 'DataBaseModel' = Relationship(back_populates='election_links')
        #     election: 'RecordElectionTypeDetails' = Relationship(back_populates='record_links')
        #     vote_method: 'RecordVotedInElection' = Relationship(back_populates='record_links')

        # class RecordDataSourceLink(SQLModel, table=True):
        #     __tablename__ = f'{self.record_type}_data_source_link'
        #     data_source_id: Optional[int] = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.record_type}_{DataSource.__tablename__}.id',
        #         primary_key=True)
        #     record_id: Optional[int] = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.validator.__tablename__}.id',
        #         primary_key=True)

        # class RecordVendorNameToTagLink(SQLModel, table=True):
        #     __tablename__ = f"{self.record_type}_vendor_tags_name_link"
        #     vendor_id: str | None = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.record_type}_vendor_name.id',
        #         primary_key=True)
        #     tag_id: str | None = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.record_type}_vendor_tags.id',
        #         primary_key=True)
        #     record_id: int | None = SQLModelField(
        #         default=None,
        #         foreign_key=f'{self.validator.__tablename__}.id',
        #         primary_key=True)
        #
        #     vendor: 'RecordVendorName' = Relationship(back_populates='tag_links')
        #     tag: 'RecordVendorTags' = Relationship(back_populates='vendor_links')
        #     record: 'DataBaseModel' = Relationship(back_populates='vendor_tag_links')

        # class RecordVendorTags(VendorTags, table=True):
        #     __tablename__ = f'{self.record_type}_vendor_tags'
        #     vendor_links: list['RecordVendorNameToTagLink'] = Relationship(
        #         back_populates='tag')
        #
        # class RecordVendorName(VendorName, table=True):
        #     __tablename__ = f'{self.record_type}_vendor_name'
        #     tag_links: list['RecordVendorNameToTagLink'] = Relationship(
        #         back_populates='vendor')
        #
        # class RecordVoterRegistration(VoterRegistration, table=True):
        #     __tablename__ = f'{self.record_type}_{VoterRegistration.__tablename__}'
        #     records: list['DataBaseModel'] = Relationship(back_populates='voter_registration')

        # class RecordAddress(Address, table=True):
        #     __tablename__ = f'{self.record_type}_{Address.__tablename__}'
        #     records: list['DataBaseModel'] = Relationship(
        #         back_populates='address_list',
        #         link_model=RecordAddressLink)
        #
        # class RecordValidatedPhoneNumber(ValidatedPhoneNumber, table=True):
        #     __tablename__ = f'{self.record_type}_{ValidatedPhoneNumber.__tablename__}'
        #     records: list['DataBaseModel'] = Relationship(
        #         back_populates='phone',
        #         link_model=RecordPhoneLink)

        # class RecordElectionTypeDetails(ElectionTypeDetails, table=True):
        #     __tablename__ = f'{self.record_type}_{ElectionTypeDetails.__tablename__}'
        #     record_links: list['RecordElectionLink'] = Relationship(back_populates='election')
        #
        # class RecordVotedInElection(VotedInElection, table=True):
        #     __tablename__ = f'{self.record_type}_{VotedInElection.__tablename__}'
        #     record_links: list['RecordElectionLink'] = Relationship(back_populates='vote_method')

        # class RecordVEPMatch(VEPMatch, table=True):
        #     __tablename__ = f'{self.record_type}_{VEPMatch.__tablename__}'
        #     records: 'DataBaseModel' = Relationship(back_populates='vep_keys')

        # class RecordDataSource(DataSource, table=True):
        #     __tablename__ = f'{self.record_type}_{DataSource.__tablename__}'
        #     records: list['DataBaseModel'] = Relationship(
        #         back_populates='data_source',
        #         link_model=RecordDataSourceLink)

        # class RecordInputData(InputData, table=True):
        #     __tablename__ = f'{self.record_type}_{InputData.__tablename__}'
        #     records: 'DataBaseModel' = Relationship(back_populates='input_data')

        # class RecordDistrict(District, table=True):
        #     __tablename__ = f"{self.record_type}_{District.__tablename__}"
        #     record_links: list['RecordDistrictLink'] = Relationship(back_populates='district')

        class DataBaseModel(SQLModel, table=True):
            __tablename__ = self.validator.__tablename__
            id: int | None = SQLModelField(
                default=None,
                primary_key=True)
            name_id: str | None = SQLModelField(
                default=None,
                foreign_key=f'{self.record_type}_{PersonName.__tablename__}.id')
            voter_registration_id: str | None = SQLModelField(
                default=None,
                foreign_key=f'{RecordVoterRegistration.__tablename__}.id'
            )
            vote_history_id: str | None = SQLModelField(
                default=None,
                foreign_key=f'{RecordVotedInElection.__tablename__}.id'
            )
            vep_keys_id: int | None = SQLModelField(
                default=None,
                foreign_key=f'{RecordVEPMatch.__tablename__}.id')
            input_data_id: int | None = SQLModelField(
                default=None,
                foreign_key=f'{RecordInputData.__tablename__}.id')

            name: RecordPersonName = Relationship(back_populates='records')
            voter_registration: 'RecordVoterRegistration' = Relationship(back_populates='records')
            address_list: list[RecordAddress] = Relationship(
                back_populates='records',
                link_model=RecordAddressLink)
            phone: list[RecordValidatedPhoneNumber] = Relationship(
                back_populates='records',
                link_model=RecordPhoneLink)
            election_links: list[RecordElectionLink] = Relationship(back_populates='record')
            vep_keys: 'RecordVEPMatch' = Relationship(back_populates='records')

            vendor_tag_links: list[RecordVendorNameToTagLink] = Relationship(
                back_populates='record')
            district_links: list[RecordDistrictLink] = Relationship(back_populates='records')
            data_source: list[RecordDataSource] = Relationship(
                back_populates='records',
                link_model=RecordDataSourceLink)
            input_data: 'RecordInputData' = Relationship(back_populates='records')

            def dump_model(self, include: set = None):
                data = {}
                if include is None or 'name' in include:
                    data['name'] = self.name
                if include is None or 'voter_registration' in include:
                    data['voter_registration'] = self.voter_registration
                if include is None or 'address_list' in include:
                    data['address_list'] = self.address_list
                if include is None or 'phone' in include:
                    data['phone'] = self.phone
                if include is None or 'district_links' in include:
                    data['district_links'] = self.district_links
                if include is None or 'election_links' in include:
                    data['election_links'] = self.election_links
                if include is None or 'vendor_tag_links' in include:
                    data['vendor_tag_links'] = self.vendor_tag_links
                if include is None or 'vep_keys' in include:
                    data['vep_keys'] = self.vep_keys
                if include is None or 'data_source' in include:
                    data['data_source'] = self.data_source
                if include is None or 'input_data' in include:
                    data['input_data'] = self.input_data
                return self.construct(**data)

        configure_mappers()

        self.tables['RecordPersonName'] = RecordPersonName
        self.tables['RecordAddressLink'] = RecordAddressLink
        self.tables['RecordPhoneLink'] = RecordPhoneLink
        self.tables['RecordDistrictLink'] = RecordDistrictLink
        self.tables['RecordElectionLink'] = RecordElectionLink
        self.tables['RecordDataSourceLink'] = RecordDataSourceLink
        self.tables['RecordVendorNameToTagLink'] = RecordVendorNameToTagLink
        self.tables['RecordVendorTags'] = RecordVendorTags
        self.tables['RecordVendorName'] = RecordVendorName
        self.tables['RecordVoterRegistration'] = RecordVoterRegistration
        self.tables['RecordAddress'] = RecordAddress
        self.tables['RecordValidatedPhoneNumber'] = RecordValidatedPhoneNumber
        self.tables['RecordElectionTypeDetails'] = RecordElectionTypeDetails
        self.tables['RecordVotedInElection'] = RecordVotedInElection
        self.tables['RecordVEPMatch'] = RecordVEPMatch
        self.tables['RecordDataSource'] = RecordDataSource
        self.tables['RecordInputData'] = RecordInputData
        self.tables['RecordDistrict'] = RecordDistrict
        self.tables['DataBaseModel'] = DataBaseModel
        SQLModel.metadata.create_all(self.engine)
        return self

    def load_record(self, record: RecordBaseModel):

        _address_list = [
            self.tables[TableEnum.RECORD_ADDRESS.value](
                **address.model_dump()
            ) for address in record.address_list
        ]

        _election_list = [
            self.tables[TableEnum.RECORD_ELECTION_LINK.value](
                election=self.tables[TableEnum.RECORD_ELECTION_TYPE_DETAILS.value](**election.model_dump()),
                vote_method=self.tables[TableEnum.RECORD_VOTED_IN_ELECTION.value](**vote.model_dump())
            )
            for vote, election in zip(record.vote_history, record.elections)
        ]

        _phone_numbers = [
            self.tables[TableEnum.RECORD_VALIDATED_PHONE_NUMBER.value](**phone.model_dump()) for phone in record.phone
        ] if record.phone else []

        _data_source = [self.tables[TableEnum.RECORD_DATA_SOURCE.value](
            **record.data_source.model_dump())] if record.data_source else []

        _vendor_tag_link_list = [
            self.tables[TableEnum.RECORD_VENDOR_NAME_TO_TAG_LINK.value](
                vendor=self.tables[TableEnum.RECORD_VENDOR_NAME.value](**vendor.model_dump()),
                tag=self.tables[TableEnum.RECORD_VENDOR_TAGS.value](**tag.model_dump())
            )
            for vendor, tag in zip(record.vendor_names, record.vendor_tags)
        ] if record.vendor_names and record.vendor_tags else []

        _districts = [
            self.tables[TableEnum.RECORD_DISTRICT.value](**district.model_dump())
            for district in record.district_set.districts
        ]

        with Session(self.engine) as session:
            for district in _districts:
                session.add(district)

            record_instance = self.tables[TableEnum.DATA_BASE_MODEL.value]()
            record_instance.name = self.tables[TableEnum.RECORD_PERSON_NAME.value](**record.name.model_dump())
            record_instance.voter_registration = self.tables[TableEnum.RECORD_VOTER_REGISTRATION.value](
                **record.voter_registration.model_dump())
            record_instance.address_list = _address_list
            record_instance.election_links = _election_list
            record_instance.phone = _phone_numbers
            record_instance.vendor_tag_links = _vendor_tag_link_list
            record_instance.data_source = _data_source
            record_instance.input_data = self.tables[TableEnum.RECORD_INPUT_DATA.value](
                **record.input_data.model_dump())
            record_instance.vep_keys = self.tables[TableEnum.RECORD_VEP_MATCH.value](**record.vep_keys.model_dump())

            session.add(record_instance)
            session.commit()

            district_links = [
                self.tables[TableEnum.RECORD_DISTRICT_LINK.value](
                    district_id=district.id,
                    record_id=record_instance.id
                )
                for district in record.district_set.districts
            ]
            for link in district_links:
                session.add(link)

            record_instance.district_links = district_links
            session.commit()

    def get_all_records(self):
        stmt = (
            select(self.tables[TableEnum.DATA_BASE_MODEL.value])
            .options(
                joinedload(self.tables[TableEnum.DATA_BASE_MODEL.value].name),
                joinedload(self.tables[TableEnum.DATA_BASE_MODEL.value].voter_registration),
                joinedload(self.tables[TableEnum.DATA_BASE_MODEL.value].address_list),
                joinedload(self.tables[TableEnum.DATA_BASE_MODEL.value].phone),
                joinedload(self.tables[TableEnum.DATA_BASE_MODEL.value].district_links)
                .joinedload(self.tables[TableEnum.RECORD_DISTRICT_LINK.value].district),
                joinedload(self.tables[TableEnum.DATA_BASE_MODEL.value].election_links)
                .joinedload(self.tables[TableEnum.RECORD_ELECTION_LINK.value].election)
                .joinedload(self.tables[TableEnum.RECORD_ELECTION_TYPE_DETAILS.value].record_links)
                .joinedload(self.tables[TableEnum.RECORD_ELECTION_LINK.value].vote_method)
                .joinedload(self.tables[TableEnum.RECORD_VOTED_IN_ELECTION.value].record_links),
                joinedload(self.tables[TableEnum.DATA_BASE_MODEL.value].vendor_tag_links)
                .joinedload(self.tables[TableEnum.RECORD_VENDOR_NAME_TO_TAG_LINK.value].tag)
                .joinedload(self.tables[TableEnum.RECORD_VENDOR_TAGS.value].vendor_links),
                joinedload(self.tables[TableEnum.DATA_BASE_MODEL.value].vep_keys),
                joinedload(self.tables[TableEnum.DATA_BASE_MODEL.value].data_source),
                joinedload(self.tables[TableEnum.DATA_BASE_MODEL.value].input_data),
            )
        )
        with Session(self.engine) as session:
            result = session.execute(stmt).unique().scalars().all()
            return result

# class DataBaseModel(SQLModel, table=True):
#     __tablename__ = self.__tablename__
#     id: int | None = SQLModelField(default=None, primary_key=True)
#     name_id: str | None = SQLModelField(default=None, foreign_key='person_name.id')
#     voter_registration_id: str | None = SQLModelField(default=None, foreign_key='voter_registration.id')
#     vote_history_id: str | None = SQLModelField(default=None, foreign_key='voted_in_election.id')
#     vep_keys_id: int | None = SQLModelField(default=None, foreign_key='vep_match.id')
#     input_data_id: int | None = SQLModelField(default=None, foreign_key='input_data.id')
