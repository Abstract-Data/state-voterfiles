from ..base import Base, mapped_column, Mapped
from typing import Optional, Dict, Any
from datetime import date
from sqlalchemy import String, JSON, Date
from sqlalchemy.orm import relationship, declared_attr


class VoterRegistrationModel(Base):
    __abstract__ = True

    vuid: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True)
    edr: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    county: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # @abstract_declared_attr
    # def record_id(cls):
    #     return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=True)

    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='voter_registration')