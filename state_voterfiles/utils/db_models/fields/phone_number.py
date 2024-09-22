from ..base import Base, mapped_column, Mapped
from typing import Optional, Dict, Any
from sqlalchemy import String, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship, declared_attr


class ValidatedPhoneNumberModel(Base):
    __abstract__ = True

    phone_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    areacode: Mapped[str] = mapped_column(String, nullable=False)
    number: Mapped[str] = mapped_column(String, nullable=False)
    reliability: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    other_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    @declared_attr
    def record_id(cls):
        return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=True)

    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='phone_numbers')
