from .base import Base, mapped_column, Mapped
from sqlalchemy import String, JSON, Boolean, Date, Integer
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from typing import Dict, Any, List
from datetime import date


class PhoneNumberModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(String, primary_key=True)
    phone_type: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    areacode: Mapped[str] = mapped_column(String, nullable=False)
    number: Mapped[str] = mapped_column(String, nullable=False)
    reliability: Mapped[str] = mapped_column(String, nullable=True)
    other_fields: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)

    def __hash__(self):
        return hash(self.id)


class AddressModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(String, primary_key=True)
    address_type: Mapped[str] = mapped_column(String, nullable=False)
    address1: Mapped[str] = mapped_column(String, nullable=False)
    address2: Mapped[str] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    zipcode: Mapped[str] = mapped_column(String, nullable=False)
    zip5: Mapped[str] = mapped_column(String, nullable=True)
    zip4: Mapped[str] = mapped_column(String, nullable=True)
    county: Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)
    standardized: Mapped[str] = mapped_column(String, nullable=True)
    other_fields: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    address_key: Mapped[str] = mapped_column(String, nullable=True)
    is_mailing: Mapped[bool] = mapped_column(Boolean, nullable=True)
    other_fields: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)

    def __hash__(self):
        return hash(self.id)


class DistrictModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(String, primary_key=True)
    state_abbv: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=True)
    county: Mapped[str] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    number: Mapped[str] = mapped_column(String, nullable=False)
    attributes: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)

    def __hash__(self):
        return hash(self.id)

    @declared_attr
    def record_associations(cls):
        return relationship('RecordBaseModel', back_populates='districts')


class VendorNameModel(Base):
    __abstract__ = True
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    def __hash__(self):
        return hash(self.id)


class ElectionDetailsModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(String, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    election_type: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=True)
    county: Mapped[str] = mapped_column(String, nullable=True)
    dates: Mapped[List[date]] = mapped_column(ARRAY(Date), nullable=True)
    desc: Mapped[str] = mapped_column(String, nullable=True)

    def __hash__(self):
        return hash(self.id)

    @declared_attr
    def voted_records(cls):
        return relationship('VotedInElectionModel', back_populates='election')
