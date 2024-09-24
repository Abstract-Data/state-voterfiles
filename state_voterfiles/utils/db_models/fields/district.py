from __future__ import annotations
from typing import Annotated, Optional, Dict, Any, List

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship, declared_attr, mapped_column, Mapped

from pydantic import Field as PydanticField

from state_voterfiles.utils.abcs.validation_model_abcs import RecordListABC, FileCategoryListABC
from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel, Base
from state_voterfiles.utils.funcs import RecordKeyGenerator


class District(RecordListABC):
    id: Optional[str] = PydanticField(default=None)
    state_abbv: Annotated[
        Optional[str],
        PydanticField(
            default=None,
            description="State abbreviation"
        )
    ]
    city: Annotated[
        Optional[str],
        PydanticField(
            default=None,
            description="City name"
        )
    ]
    county: Annotated[
        Optional[str],
        PydanticField(
            default=None,
            description="County name"
        )
    ]
    type: Annotated[
        str,
        PydanticField(
            ...,
            description="Type of district (e.g., 'city', 'county', 'court', 'state', 'federal')"
        )
    ]
    name: Annotated[
        Optional[str],
        PydanticField(
            default=None,
            description="Name of the district"
        )
    ]
    number: Annotated[
        Optional[str],
        PydanticField(
            default=None,
            description="Number or ID of the district"
        )
    ]
    attributes: Annotated[
        Dict[str, Any],
        PydanticField(
            default_factory=dict,
            description="Additional attributes specific to the district type"
        )
    ]
    record_associations: Annotated[
        Optional[List['RecordDistrict']],
        PydanticField(
            default=None
        )
    ]

    def generate_hash_key(self) -> str:
        _make_key = RecordKeyGenerator.generate_static_key
        if self.city:
            self.id = _make_key((self.state_abbv, self.city, self.type, self.name, self.number))
        elif self.county:
            self.id = _make_key((self.state_abbv, self.county, self.type, self.name, self.number))
        else:
            self.id = _make_key((self.state_abbv, self.type, self.name, self.number))

        return self.id

    def update(self, other: District):
        if other.city and not self.city:
            self.city = other.city
        if other.county and not self.county:
            self.county = other.county
        if other.name and not self.name:
            self.name = other.name
        if other.number and not self.number:
            self.number = other.number
        if other.attributes:
            self.attributes.update(other.attributes)

class RecordDistrict(ValidatorBaseModel):

    district_id: Annotated[Optional[str], PydanticField(default=None, description="ID of the district")]
    district: Annotated[Optional['District'], PydanticField(default=None, description="District information")]
    record_id: Annotated[Optional[int], PydanticField(default=None, description="ID of the record")]
    record: Annotated[Optional['RecordBaseModel'], PydanticField(default=None, description="Record information")]


class RecordDistrictModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(ForeignKey('districts.id'), nullable=False)

    district: Mapped['DistrictModel'] = relationship("District", back_populates="record_associations")

    @declared_attr
    def record_id(cls):
        return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=False)

    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='government_districts')
