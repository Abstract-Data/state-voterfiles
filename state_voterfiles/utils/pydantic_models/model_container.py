# from typing import Tuple
# from pydantic.dataclasses import dataclass as pydantic_dataclass, Field as PydanticField
# from sqlmodel import SQLModel, Field as SQLModelField, Session
# from sqlalchemy import Engine
# from state_voterfiles.utils.pydantic_models.cleanup_model import *
# from state_voterfiles.utils.db_models.record import RecordBaseModel
# from state_voterfiles.utils.db_models.fields.elections import ElectionLink, ElectionLinkToRecord
# from state_voterfiles.utils.db_models.fields.district import DistrictLink
# from state_voterfiles.utils.db_models.fields.vendor import VendorTagsToVendorLink
#
# TABLE_OBJECTS = [
#     RecordBaseModel,
#     PersonName,
#     VendorName,
#     VendorTags,
#     VoterRegistration,
#     Address,
#     AddressLink,
#     ValidatedPhoneNumber,
#     ElectionTypeDetails,
#     VotedInElection,
#     ElectionLink,
#     ElectionLinkToRecord,
#     DataSource,
#     DataSourceLink,
#     District,
#     DistrictLink,
#     DistrictLinkToRecord,
#     InputData,
#     VEPMatch
# ]
#
#
# @pydantic_dataclass(config={"arbitrary_types_allowed": True})
# class ValidationModelContainer:
#     record_type: str
#
#     # def __post_init__(self):
#     #     self._establish_table_relationships()
#
#     # def _establish_table_relationships(self):
#     #     for table in TABLE_OBJECTS:
#     #         TableNameManager.set_table_name(table, f"{self.record_type}_{table.__name__.lower()}")
#     #     configure_mappers()
#     #     return self
#         # Address.records = Relationship(
#         #     back_populates='address_list',
#         #     link_model=AddressLink)
#         #
#         # AddressLink.address_id = SQLModelField(
#         #     default=None,
#         #     foreign_key=f"{Address.__tablename__}.id",
#         #     primary_key=True)
#         # AddressLink.record_id = SQLModelField(
#         #     default=None,
#         #     foreign_key=f'f{RecordBaseModel.__tablename__}.id',
#         #     primary_key=True)
#         #
#         # PhoneLink.record_id = SQLModelField(
#         #     default=None,
#         #     foreign_key=f'{RecordBaseModel.__tablename__}.id',
#         #     primary_key=True)
#         #
#         # ValidatedPhoneNumber.records = Relationship(
#         #     back_populates='phone',
#         #     link_model=PhoneLink)
#         #
#         # VendorTags.vendors = Relationship(back_populates="tags", link_model=VendorTagsToVendorLink)
#         # VendorName.tags = Relationship(back_populates="vendors", link_model=VendorTagsToVendorLink)
#         #
#         # VendorTagsToVendorToRecordLink.record_id = SQLModelField(default=None, foreign_key="record_base.id", primary_key=True)
#         # VendorTagsToVendorToRecordLink.record = Relationship(back_populates='vendor_tag_record_links')
#         #
#         # # # Relationships from elections.py
#         # ElectionLinkToRecord.record_id = SQLModelField(
#         #     default=None,
#         #     foreign_key=f'{RecordBaseModel.__tablename__}.id',
#         #     primary_key=True)
#         # ElectionLinkToRecord.record = Relationship(back_populates="election_link_records")
#         #
#         # # Relationships from data_source.py
#         # DataSource.records = Relationship(
#         #     back_populates='data_source',
#         #     link_model=DataSourceLink)
#         #
#         # DataSourceLink.record_id = SQLModelField(
#         #     default=None,
#         #     foreign_key=f'{RecordBaseModel.__tablename__}.id',
#         #     primary_key=True)
#         #
#         # # Relationships from district.py
#         # DistrictLink.record_id = SQLModelField(
#         #     default=None,
#         #     foreign_key=f"{RecordBaseModel.__tablename__}.id",
#         #     primary_key=True)
#         # DistrictLinkToRecord.record_id = SQLModelField(
#         #     default=None,
#         #     foreign_key=f"{RecordBaseModel.__tablename__}.id",
#         #     primary_key=True)
#         # DistrictLinkToRecord.record = Relationship(back_populates="district_link_records")
#         # configure_mappers()
#         # return self
#
#     def create_tables(self, engine: Engine):
#         SQLModel.metadata.create_all(engine)
#         self.engine_ = engine
#         return self
#
#     # def set_relationships(self, engine: Engine):
#     #     with Session(engine) as session:
#     #         _cleanup = self.cleanup_model
#     #         _final = self.final_model
#     #
#     #         _final.name = _cleanup.name
#     #         _final.voter_registration = _cleanup.voter_registration
#     #         session.add(_final)
#     #
#     #         _addresses = [x for x in _cleanup.address_list] if _cleanup.address_list else []
#     #         _data_source = [_cleanup.data_source] if _cleanup.data_source else []
#     #         _phone_numbers = [_cleanup.phone] if _cleanup.phone else []
#     #         _districts = [_cleanup.district_set] if _cleanup.district_set else []
#     #
#     #         for vote_details in _cleanup.vote_history:
#     #             _election_to_vote_link = ElectionLink(
#     #                 election_id=vote_details.election_id,
#     #                 vote_details_id=vote_details.id
#     #             )
#     #             _election_to_record_link = ElectionLinkToRecord(
#     #                 election_link_id=_election_to_vote_link.election_id,
#     #                 record_id=_final.id
#     #             )
#     #             session.add(_election_to_record_link)
#     #
#     #         _district_link = [
#     #             DistrictLink(
#     #                 district_id=x.id,
#     #                 record_id=_final.id
#     #             ) for x in _districts
#     #         ] if _districts else []
#     #
#     #         _vendor_names_link = [
#     #             VendorTagsToVendorLink(
#     #                 vendor_id=x.id,
#     #                 tag_id=_final.id
#     #             ) for x in _cleanup.vendor_names
#     #         ] if _cleanup.vendor_names else []
#     #
#     #         _vendor_tags_link = [
#     #             VendorTagsToVendorLink(
#     #                 vendor_id=x.id,
#     #                 tag_id=_final.id
#     #             ) for x in _cleanup.vendor_tags
#     #         ] if _cleanup.vendor_tags else []
