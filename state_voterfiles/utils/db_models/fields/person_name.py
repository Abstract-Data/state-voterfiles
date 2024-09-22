from ..base import Base, mapped_column, Mapped
from typing import Optional, Dict, Any
from datetime import date
from sqlalchemy import String, JSON, Date
from sqlalchemy.orm import relationship, declared_attr


class PersonNameModel(Base):
    __abstract__ = True

    prefix: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first: Mapped[str] = mapped_column(String, nullable=False)
    last: Mapped[str] = mapped_column(String, nullable=False)
    middle: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    suffix: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    other_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # @abstract_declared_attr
    # def record_id(cls):
    #     return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=True)

    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='name')