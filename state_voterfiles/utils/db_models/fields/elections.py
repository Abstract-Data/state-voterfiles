
from enum import Enum as PyEnum
from ..base import Base, mapped_column, Mapped
from typing import Optional
from datetime import date
from sqlalchemy import String, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy import Enum as SA_Enum


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


class VotedInElectionModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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
        return hash((self.election_id, self.record_id, self.vote_date))
