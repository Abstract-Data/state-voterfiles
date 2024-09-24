from __future__ import annotations
from typing import Optional, Dict, Any, Annotated
from sqlalchemy import String, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship, declared_attr, mapped_column, Mapped

from pydantic import Field as PydanticField
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber

from state_voterfiles.utils.abcs.validation_model_abcs import RecordListABC
from state_voterfiles.utils.funcs import RecordKeyGenerator
from state_voterfiles.utils.db_models.model_bases import Base


class ValidatedPhoneNumber(RecordListABC):
    id: Optional[str] = PydanticField(default=None)
    phone_type: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    phone: Annotated[
        PydanticPhoneNumber,
        PydanticField()
    ]
    areacode: Annotated[
        str,
        PydanticField(),
    ]
    number: Annotated[
        str,
        PydanticField(),
    ]
    reliability: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    other_fields: Annotated[
        Optional[Dict[str, Any]],
        PydanticField(default_factory=dict)
    ]

    def generate_hash_key(self) -> str:
        return RecordKeyGenerator.generate_static_key(self.phone)

    def update(self, other: ValidatedPhoneNumber):
        self.phone_type = other.phone_type
        self.phone = other.phone
        self.areacode = other.areacode
        self.number = other.number
        self.reliability = other.reliability
        self.other_fields = other.other_fields


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
