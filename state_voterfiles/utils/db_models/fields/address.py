from ..base import Base, mapped_column, Mapped
from typing import Optional, Dict, Any
from sqlalchemy import String, JSON, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declared_attr


class AddressModel(Base):
    __abstract__ = True
    address_type: Mapped[str] = mapped_column(String, nullable=False)
    address1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    zipcode: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    zip5: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    zip4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    county: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    standardized: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address_parts: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    address_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_mailing: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    other_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    @declared_attr
    def record_id(cls):
        return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=True)

    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='address_list')
