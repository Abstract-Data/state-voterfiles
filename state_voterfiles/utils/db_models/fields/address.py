from __future__ import annotations
from typing import Optional, Dict, Any, Annotated

from ..model_bases import ValidatorBaseModel
from pydantic import Field as PydanticField
from sqlmodel import Field as SQLModelField
from state_voterfiles.utils.funcs import RecordKeyGenerator


class Address(ValidatorBaseModel):
    """
    This should be used for all addresses, you'll need to pass a dictionary of the address fields to the model, versus all values
    """
    id: str | None = SQLModelField(default=None)
    address_type: str | None = SQLModelField(default=None)
    address1: str | None = SQLModelField(default=None)
    address2: str | None = SQLModelField(default=None)
    city: str | None = SQLModelField(default=None)
    state: str | None = SQLModelField(default=None)
    zipcode: str | None = SQLModelField(default=None, regex=r'^\d{5}(-\d{4})?$')
    zip5: str | None = SQLModelField(default=None, max_length=5, min_length=5)
    zip4: str | None = SQLModelField(default=None, max_length=4, min_length=4)
    county: str | None = SQLModelField(default=None)
    country: str | None = SQLModelField(default=None)
    standardized: str | None = SQLModelField(default=None)
    address_parts: Dict[str, Any] | None = SQLModelField(default=None)
    address_key: str | None = SQLModelField(default=None)
    is_mailing: bool | None = SQLModelField(default=None)
    other_fields: Dict[str, Any] | None = SQLModelField(default=None),

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.standardized)

    def __eq__(self, other):
        return self.standardized == other.standardized

    def generate_hash_key(self) -> str:
        if not self.standardized:
            raise ValueError("Address must be standardized before generating a hash key.")
        return RecordKeyGenerator.generate_static_key(self.standardized)

    def update(self, other: Address):
        if other.address1 and not self.address1:
            self.address1 = other.address1
        if other.address2 and not self.address2:
            self.address2 = other.address2
        if other.city and not self.city:
            self.city = other.city
        if other.state and not self.state:
            self.state = other.state
        if other.zipcode and not self.zipcode:
            self.zipcode = other.zipcode
        if other.zip5 and not self.zip5:
            self.zip5 = other.zip5
        if other.zip4 and not self.zip4:
            self.zip4 = other.zip4
        if other.county and not self.county:
            self.county = other.county
        if other.country and not self.country:
            self.country = other.country
        if other.standardized and not self.standardized:
            self.standardized = other.standardized
        if other.address_parts and not self.address_parts:
            self.address_parts = other.address_parts
        if other.address_key and not self.address_key:
            self.address_key = other.address_key
        if other.is_mailing and not self.is_mailing:
            self.is_mailing = other.is_mailing
        if other.other_fields:
            self.other_fields.update(other.other_fields)


# class AddressModel(Base):
#     __abstract__ = True
#     address_type: Mapped[str] = mapped_column(String, nullable=False)
#     address1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     zipcode: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     zip5: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
#     zip4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
#     county: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     country: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     standardized: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     address_parts: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
#     address_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     is_mailing: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
#     other_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def record_id(cls):
#         return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def record(cls):
#         return relationship('RecordModel', back_populates='address_list')
