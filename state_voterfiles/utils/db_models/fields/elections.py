from __future__ import annotations
import abc
from enum import Enum as PyEnum
from typing import Optional, Annotated, List, Set
from datetime import date
from sqlalchemy import Enum as SA_Enum

from pydantic import Field as PydanticField
from sqlmodel import Field as SQLModelField

from state_voterfiles.utils.funcs import RecordKeyGenerator
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
from state_voterfiles.utils.validation.election_history_codes import VoteMethodCodes


class ElectionType(PyEnum):
    GE = 'GE'
    PE = 'PE'
    ME = 'ME'
    SE = 'SE'
    RE = 'RE'
    PR = 'PR'
    OP = 'OP'
    CP = 'CP'
    NP = 'NP'
    SB = 'SB'
    JE = 'JE'
    LE = 'LE'
    CE = 'CE'
    RF = 'RF'
    PP = 'PP'
    PPR = 'PPR'
    PC = 'PC'


class VoteMethod(PyEnum):
    IP = 'IP'
    MI = 'MI'
    EV = 'EV'
    PV = 'PV'
    AB = 'AB'


# Use SQLAlchemy's Enum to create a database column type from the Python Enum
ElectionTypeDB = SA_Enum(ElectionType, name='election_types', native_enum=False)
VoteMethodDB = SA_Enum(VoteMethod, name='vote_methods', native_enum=False)


class ElectionTypeDetails(ValidatorConfig):
    id: str =  SQLModelField(default_factory=lambda: '')
    year: int = SQLModelField(...)
    election_type: str = SQLModelField(...)
    state: str = SQLModelField(...)
    city: str | None = SQLModelField(default=None)
    county: str | None = SQLModelField(default=None)
    dates: set[date] | None = SQLModelField(default=None)
    desc: str | None = SQLModelField(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, ElectionTypeDetails):
            return self.id == other.id
        return False

    def generate_hash_key(self) -> str:
        # Create a string with the essential properties of the election
        key_string = f"{self.state}"
        if self.city:
            key_string += f"-{self.city}"
        if self.county:
            key_string += f"-{self.county}"
        key_string += f"-{self.year}-{self.election_type}"
        # if self.dates:
        #     key_string += f"_{'_'.join(sorted(d.isoformat() for d in self.dates))}"

        # # Generate a SHA256 hash of the key string
        # self.id = RecordKeyGenerator.generate_static_key(key_string)  # Using first 16 characters for brevity
        self.id = key_string
        return self.id

    def update(self, other: ElectionTypeDetails):
        if other.city and not self.city:
            self.city = other.city
        if other.county and not self.county:
            self.county = other.county
        if other.dates and not self.dates:
            self.dates = other.dates
        if other.desc and not self.desc:
            self.desc = other.desc


class VotedInElection(ValidatorConfig):
    id: str | None = SQLModelField(default=None)
    # year: Annotated[int, PydanticField(...)]
    party: str | None = SQLModelField(default=None)
    vote_date: date | None = SQLModelField(default=None)
    vote_method: VoteMethodCodes | None = SQLModelField(default=None)
    # election_id: Annotated[Optional[str], PydanticField(default=None)]
    voter: VoterRegistration | None = SQLModelField(default=None)
    # record_id: Annotated[Optional[int], PydanticField(default=None)]
    # record: Annotated[Optional['RecordBaseModel'], PydanticField(default=None)]
    election_id: str = SQLModelField(...)
    election: ElectionTypeDetails = SQLModelField(...)

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def generate_hash_key(self) -> str:
        key_string: str = f"{self.election_id}"
        if self.party:
            key_string += f"-{self.party}"
        if self.vote_method:
            key_string += f"-{self.vote_method}"
        if self.vote_date:
            key_string += f"-{self.vote_date:  %Y%m%d}"

        return key_string

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
