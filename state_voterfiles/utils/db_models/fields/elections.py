from __future__ import annotations
from enum import Enum as PyEnum
from typing import Optional, Annotated, List, Set
from datetime import date

from sqlalchemy import String, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship, declared_attr, Mapped, mapped_column
from sqlalchemy import Enum as SA_Enum

from pydantic import Field as PydanticField

from state_voterfiles.utils.db_models.model_bases import Base
from state_voterfiles.utils.funcs import RecordKeyGenerator
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig


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
    id: str = PydanticField(default_factory=lambda: '')
    year: int
    election_type: str
    state: str
    city: Optional[str] = None
    county: Optional[str] = None
    dates: Optional[Set[date]] = PydanticField(default=None)
    desc: Optional[str] = None
    voted_records: Optional[List[VotedInElection]] = PydanticField(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, ElectionTypeDetails):
            return self.id == other.id
        return False

    def generate_hash_key(self) -> str:
        # Create a string with the essential properties of the election
        key_string = f"{self.year}_{self.election_type}_{self.state}"
        if self.city:
            key_string += f"_{self.city}"
        if self.county:
            key_string += f"_{self.county}"
        # if self.dates:
        #     key_string += f"_{'_'.join(sorted(d.isoformat() for d in self.dates))}"

        # Generate a SHA256 hash of the key string
        return RecordKeyGenerator.generate_static_key(key_string)  # Using first 16 characters for brevity

    def update(self, other: ElectionTypeDetails):
        if other.dates:
            self.dates.update(other.dates)
        if other.city and not self.city:
            self.city = other.city
        if other.county and not self.county:
            self.county = other.county


class VotedInElection(ValidatorConfig):
    id: Annotated[Optional[str], PydanticField(default=None)]
    year: Annotated[int, PydanticField(...)]
    party: Annotated[Optional[str], PydanticField(default=None)]
    vote_date: Annotated[Optional[date], PydanticField(default=None)]
    vote_method: Annotated[Optional[str], PydanticField(default=None)]
    election_id: Annotated[Optional[str], PydanticField(default=None)]
    record_vuid: Annotated[Optional[str], PydanticField(default=None)]
    record_id: Annotated[Optional[int], PydanticField(default=None)]
    record: Annotated[Optional['RecordBaseModel'], PydanticField(default=None)]
    election: Annotated[Optional[ElectionTypeDetails], PydanticField(default=None)]

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def generate_hash_key(self) -> str:
        key_string = f"{self.election_id}_{self.record_id}_{self.vote_date}"
        if self.vote_method:
            key_string += f"_{self.vote_method}"
        if self.party:
            key_string += f"_{self.party}"
        return RecordKeyGenerator.generate_static_key(key_string)


class RecordElectionVote(ValidatorConfig):
    id: Optional[str] = None
    vote_detail_id: str

    election_desc: Optional[VotedInElection] = None


class VotedInElectionModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    party: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    vote_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    vote_method: Mapped[VoteMethod] = mapped_column(VoteMethodDB, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    @declared_attr
    def election_id(cls) -> Mapped[int]:
        return mapped_column(Integer, ForeignKey('election_types.id'), nullable=False)

    @declared_attr
    def election(cls):
        return relationship("ElectionType", back_populates="voted_records")

    @declared_attr
    def record_vuid(cls) -> Mapped[Optional[str]]:
        return mapped_column(String, ForeignKey('record.vuid'), nullable=True)

    @declared_attr
    def record_id(cls) -> Mapped[int]:
        return mapped_column(Integer, ForeignKey(f'{cls.__tablename__.replace("election_history", "")}.id'),
                             nullable=False)

    @declared_attr
    def record(cls):
        return relationship(cls.__tablename__.replace("election_history", ""), back_populates="election_history")

    def __hash__(self):
        return hash(self.id)


class RecordElectionVoteModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    vote_detail_id: Mapped[str] = mapped_column(String, ForeignKey('voted_in_election.id'), nullable=False)

    @declared_attr
    def election_desc(cls):
        return relationship("VotedInElection", back_populates="election_desc")
