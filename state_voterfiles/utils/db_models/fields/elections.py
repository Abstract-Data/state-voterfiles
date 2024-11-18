from typing import Optional
from datetime import date, datetime

from pydantic.dataclasses import dataclass as pydantic_dataclass
# from sqlmodel import Field as SQLModelField, JSON, Relationship, UniqueConstraint, Column, DateTime, func, text
from sqlalchemy import Enum as SA_Enum
from sqlalchemy.dialects.postgresql import TIMESTAMP

from state_voterfiles.utils.db_models.model_bases import SQLModelBase
from election_utils.election_history_codes import (
    ElectionTypeCodesBase,
    VoteMethodCodesBase,
    PoliticalPartyCodesBase
)
#
# from election_utils.election_models import (
#     ElectionTypeDetailsBase,
#     ElectionVoteMethodBase,
#     ElectionVoteBase,
#     ElectionDataTuple
# )
#
#
# class ElectionTypeDetails(ElectionTypeDetailsBase, table=True):
#     election_vote_methods: list["ElectionVoteMethod"] = Relationship(
#         back_populates="vote_method_election",
#         # link_model=ElectionAndVoteMethodLink
#     )
#     election_voters: list["ElectionVote"] = Relationship(
#         back_populates="election"
#     )
#
#
# class ElectionVoteMethod(ElectionVoteMethodBase, table=True):
#     vote_method_votes: list["ElectionVote"] = Relationship(back_populates="vote_method")
#     vote_method_election: list["ElectionTypeDetails"] = Relationship(
#         back_populates="election_vote_methods",
#         # link_model=ElectionAndVoteMethodLink
#     )
#
#
# class ElectionVote(ElectionVoteBase, table=True):
#     election: ElectionTypeDetails = Relationship(back_populates="election_voters")
#     vote_method: ElectionVoteMethod = Relationship(back_populates="vote_method_votes")
#     record: "RecordBaseModel" = Relationship(
#         back_populates="vote_history",
#     )


# @pydantic_dataclass
# class ElectionDataTuple:
#     election: "ElectionTypeDetails"
#     vote_method: "ElectionVoteMethod"
#     vote_record: "ElectionVote"
#
#
# # Use SQLAlchemy's Enum to create a database column type from the Python Enum
# ElectionTypeDB = SA_Enum(ElectionTypeCodes, name='election_types', native_enum=False)
# VoteMethodDB = SA_Enum(VoteMethodCodes, name='vote_methods', native_enum=False)
# PolitcalPartyDB = SA_Enum(PoliticalPartyCodes, name='political_parties', native_enum=False)


# TODO: Create an Election and Vote Type Table, then create a vote_type link table that links the election and vote_type to the record

# class ElectionAndVoteMethodLink(SQLModelBase, table=True):
#     election_id: Optional[str] = SQLModelField(foreign_key="electiontypedetails.id", primary_key=True)
#     vote_method_id: Optional[str] = SQLModelField(foreign_key="electionvotemethod.id", primary_key=True)


# class ElectionAndVoterLink(SQLModelBase, table=True):
#     record_voter_id: str = SQLModelField(foreign_key="recordbasemodel.voter_registration_id", primary_key=True)
#     election_vote_id: int = SQLModelField(foreign_key="electionvote.id", primary_key=True)


# class ElectionTypeDetails(SQLModelBase, table=True):
#     id: str = SQLModelField(default_factory=lambda: '', primary_key=True)
#     year: int = SQLModelField(...)
#     election_type: ElectionTypeCodes = SQLModelField(sa_column=ElectionTypeDB)
#     state: str = SQLModelField(...)
#     city: str | None = SQLModelField(default=None, nullable=True)
#     county: str | None = SQLModelField(default=None, nullable=True)
#     dates: set[date] | None = SQLModelField(default=None, sa_type=JSON)
#     desc: str | None = SQLModelField(default=None, nullable=True)
#     created_at: datetime = SQLModelField(
#         sa_column=Column(DateTime(timezone=True), server_default=func.now()),
#         default=None
#     )
#     updated_at: datetime = SQLModelField(
#         sa_column=Column(
#             DateTime(timezone=True),
#             server_default=func.now(),
#             onupdate=func.now()
#         ),
#         default=None
#     )
#     election_vote_methods: list["ElectionVoteMethod"] = Relationship(
#         back_populates="vote_method_election",
#         # link_model=ElectionAndVoteMethodLink
#     )
#     election_voters: list["ElectionVote"] = Relationship(
#         back_populates="election"
#     )
#
#     def __init__(self, **data):
#         super().__init__(**data)
#         self.generate_hash_key()
#
#     def __hash__(self):
#         return hash(self.id)
#
#     def __eq__(self, other):
#         if isinstance(other, ElectionTypeDetails):
#             return self.id == other.id
#         return False
#
#     def generate_hash_key(self) -> str:
#         # Create a string with the essential properties of the election
#         key_string = f"{self.state}"
#         if self.city:
#             key_string += f"-{self.city}"
#         if self.county:
#             key_string += f"-{self.county}"
#         key_string += f"-{self.year}-{self.election_type.value}"
#         # if self.dates:
#         #     key_string += f"_{'_'.join(sorted(d.isoformat() for d in self.dates))}"
#
#         # # Generate a SHA256 hash of the key string
#         # self.id = RecordKeyGenerator.generate_static_key(key_string)  # Using first 16 characters for brevity
#         self.id = key_string.replace(" ", "")
#         return self.id
#
#     def update(self, other: 'ElectionTypeDetails'):
#         if other.city and not self.city:
#             self.city = other.city
#         if other.county and not self.county:
#             self.county = other.county
#         if other.dates and not self.dates:
#             self.dates = other.dates
#         if other.desc and not self.desc:
#             self.desc = other.desc
#         for _method in self.vote_methods:
#             for other_method in other.vote_methods:
#                 if _method.vote_method == other_method.vote_method:
#                     _method.votes.extend(other_method.votes)
#                     break
#                 else:
#                     self.vote_methods.append(other_method)
#
#     def add_voter_or_update(self, vote_entry: "VotedInElection"):
#         for voter in self.voters:
#             if voter.id == vote_entry.id:
#                 return
#         self.voters.append(vote_entry)
#
#
# class ElectionVoteMethod(SQLModelBase, table=True):
#     id: str = SQLModelField(primary_key=True)
#     party: Optional[PoliticalPartyCodes] = SQLModelField(default=None, sa_column=PolitcalPartyDB)
#     vote_date: Optional[date] = SQLModelField(default=None, nullable=True)
#     vote_method: VoteMethodCodes = SQLModelField(sa_column=VoteMethodDB)
#     election_id: str = SQLModelField(foreign_key="electiontypedetails.id", unique=False)
#     created_at: datetime = SQLModelField(
#         sa_column=Column(
#             TIMESTAMP(timezone=True),
#             server_default=text("CURRENT_TIMESTAMP")
#         )
#     )
#     updated_at: datetime = SQLModelField(
#         sa_column=Column(
#             TIMESTAMP(timezone=True),
#             server_default=text("CURRENT_TIMESTAMP"),
#             server_onupdate=text("CURRENT_TIMESTAMP"),
#         ),
#         default=None
#     )
#     vote_method_votes: list["ElectionVote"] = Relationship(back_populates="vote_method")
#     vote_method_election: list[ElectionTypeDetails] = Relationship(
#         back_populates="election_vote_methods",
#         # link_model=ElectionAndVoteMethodLink
#     )
#     def __init__(self, **data):
#         super().__init__(**data)
#         self.id = self.generate_hash_key()
#
#     def __hash__(self):
#         return hash(self.id)
#
#     def generate_hash_key(self) -> str:
#         key_string: str = f"{self.election_id}"
#         if self.vote_method:
#             key_string += f"-{self.vote_method.value}"
#         if self.vote_date:
#             key_string += f"-{self.vote_date:  %Y%m%d}"
#         if self.party:
#             key_string += f"-{self.party.value}"
#
#         return key_string
#
#
# class ElectionVote(SQLModelBase, table=True):
#     # id: Optional[int] = SQLModelField(primary_key=True)
#     __table_args__ = (UniqueConstraint('voter_id', 'election_id', 'vote_method_id'),)
#     voter_id: Optional[str] = SQLModelField(foreign_key="recordbasemodel.voter_registration_id", primary_key=True)
#     election_id: str = SQLModelField(foreign_key="electiontypedetails.id", primary_key=True)
#     vote_method_id: str = SQLModelField(foreign_key="electionvotemethod.id", primary_key=True)
#     created_at: datetime = SQLModelField(
#         sa_column=Column(
#             TIMESTAMP(timezone=True),
#             server_default=text("CURRENT_TIMESTAMP")
#         )
#     )
#     updated_at: datetime = SQLModelField(
#         sa_column=Column(
#             TIMESTAMP(timezone=True),
#             server_default=text("CURRENT_TIMESTAMP"),
#             server_onupdate=text("CURRENT_TIMESTAMP"),
#         ),
#         default=None
#     )
#     election: ElectionTypeDetails = Relationship(back_populates="election_voters")
#     vote_method: ElectionVoteMethod = Relationship(back_populates="vote_method_votes")
#     record: "RecordBaseModel" = Relationship(
#         back_populates="vote_history",
        # link_model=ElectionAndVoterLink,
        # sa_relationship_kwargs={
        #     'primaryjoin': 'ElectionVote.id == ElectionAndVoterLink.election_vote_id',
        #     'secondaryjoin': 'ElectionAndVoterLink.record_voter_id == RecordBaseModel.voter_registration_id'
        # }
    # )

# class ElectionTypeModel(Base):
#     __abstract__ = True
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     year: Mapped[int] = mapped_column(Integer, nullable=False)
#     election_type: Mapped[ElectionType] = mapped_column(ElectionTypeDB, nullable=False)
#     state: Mapped[str] = mapped_column(String, nullable=False)
#     city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     county: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     dates: Mapped[Set[date]] = mapped_column(JSON, nullable=True)
#     desc: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def voted_in_election(cls):
#         return relationship("VotedInElection", back_populates="election")


# class VotedInElectionModel(Base):
#     __abstract__ = True
#
#     id: Mapped[str] = mapped_column(Integer, primary_key=True)
#     party: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     vote_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
#     vote_method: Mapped[VoteMethod] = mapped_column(VoteMethodDB, nullable=False)
#
#     @declared_attr
#     @abc.abstractmethod
#     def election_id(cls) -> Mapped[int]:
#         return mapped_column(Integer, ForeignKey('election_types.id'), nullable=False)
#
#     @declared_attr
#     @abc.abstractmethod
#     def election(cls):
#         return relationship("ElectionType", back_populates="voted_in_election")
#
#     @declared_attr
#     @abc.abstractmethod
#     def record_id(cls) -> Mapped[int]:
#         return mapped_column(Integer, ForeignKey(f'{cls.__tablename__.replace("election_history", "")}.id'),
#                              nullable=False)
#
#     @declared_attr
#     @abc.abstractmethod
#     def record(cls):
#         return relationship(cls.__tablename__.replace("election_history", ""), back_populates="election_history")
#
#     def __hash__(self):
#         return hash(self.id)
