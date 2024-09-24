from typing import Optional, Dict, Any
from datetime import date

from sqlalchemy import String, JSON, Date
from sqlalchemy.orm import relationship, declared_attr, mapped_column, Mapped

from pydantic import Field as PydanticField
from pydantic.types import PastDate

from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel, Base
from state_voterfiles.utils.funcs import RecordKeyGenerator


class PersonName(ValidatorBaseModel):
    id: Optional[str] = PydanticField(default=None)
    prefix: Optional[str] = PydanticField(default=None)
    first: Optional[str] = PydanticField(default=None)
    last: Optional[str] = PydanticField(default=None)
    middle: Optional[str] = PydanticField(default=None)
    suffix: Optional[str] = PydanticField(default=None)
    dob: Optional[PastDate] = PydanticField(default=None)
    gender: Optional[str] = PydanticField(default=None, max_length=1)
    other_fields: Optional[Dict[str, Any]] = PydanticField(default=None)

    def __hash__(self):
        return hash(self.id)

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def generate_hash_key(self) -> str:
        return RecordKeyGenerator.generate_static_key((self.first, self.last, self.dob))


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