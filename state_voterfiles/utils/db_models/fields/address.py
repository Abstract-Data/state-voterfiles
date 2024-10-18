from typing import Optional, Dict, Any, ForwardRef
from datetime import datetime

from sqlmodel import Field as SQLModelField, JSON, Relationship, SQLModel, Column, DateTime, func

from state_voterfiles.utils.funcs.record_keygen import RecordKeyGenerator
from state_voterfiles.utils.db_models.model_bases import SQLModelBase


RecordBaseModel = ForwardRef("RecordBaseModel")


class AddressLink(SQLModel, table=True):
    __tablename__ = 'address_link'
    address_id: str | None = SQLModelField(default=None, foreign_key=f"address.id", primary_key=True)
    record_id: Optional[int] = SQLModelField(default=None, foreign_key="recordbasemodel.id", primary_key=True)


class Address(SQLModelBase, table=True):
    """
    This should be used for all addresses, you'll need to pass a dictionary of the address fields to the model, versus all values
    """
    id: str | None = SQLModelField(default=None, primary_key=True)
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
    address_parts: Dict[str, Any] | None = SQLModelField(default=None, sa_type=JSON)
    address_key: str | None = SQLModelField(default=None)
    is_mailing: bool | None = SQLModelField(default=None)
    is_residence: bool | None = SQLModelField(default=None)
    other_fields: Dict[str, Any] | None = SQLModelField(default=None, sa_type=JSON)
    records: list[RecordBaseModel] = Relationship(back_populates='address_list', link_model=AddressLink)
    created_at: datetime = SQLModelField(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        default=None
    )
    updated_at: datetime = SQLModelField(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        ),
        default=None
    )

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

    def update(self, other: "Address"):
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


