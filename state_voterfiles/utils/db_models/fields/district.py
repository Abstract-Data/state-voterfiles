from __future__ import annotations
from typing import Annotated, Optional, Dict, Any

from pydantic import Field as PydanticField
from sqlmodel import Field as SQLModelField, JSON

from state_voterfiles.utils.abcs.validation_model_abcs import RecordListABC, FileCategoryListABC
from state_voterfiles.utils.funcs import RecordKeyGenerator


class District(RecordListABC):
    id: Optional[str] = PydanticField(default=None)
    state_abbv: str | None = SQLModelField(default=None, description="State abbreviation")
    city: str | None = SQLModelField(default=None, description="City name")
    county: str | None = SQLModelField(default=None, description="County name")
    type: str = SQLModelField(
            ...,
            description="Type of district (e.g., 'city', 'county', 'court', 'state', 'federal')"
        )
    name: str | None = SQLModelField(default=None, description="Name of the district")
    number: str | None = SQLModelField(default=None, description="Number or ID of the district")
    attributes: Dict[str, Any] | None = SQLModelField(
        default_factory=dict,
        description="Additional attributes specific to the district type",
        sa_type=JSON
    )

    def generate_hash_key(self) -> str:
        _make_key = RecordKeyGenerator.generate_static_key
        if self.city:
            self.id = _make_key((self.state_abbv, self.city, self.type, self.name, self.number))
        elif self.county:
            self.id = _make_key((self.state_abbv, self.county, self.type, self.name, self.number))
        else:
            self.id = _make_key((self.state_abbv, self.type, self.name, self.number))

        return self.id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, District):
            return self.id == other.id
        return False
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

# class DistrictModel(Base):
#     __abstract__ = True
#
#     id: Mapped[str] = mapped_column(Integer, primary_key=True)
#     state_abbv: Mapped[str] = mapped_column(String, nullable=True)
#     city: Mapped[str] = mapped_column(String, nullable=True)
#     county: Mapped[str] = mapped_column(String, nullable=True)
#     type: Mapped[str] = mapped_column(String, nullable=False)
#     name: Mapped[str] = mapped_column(String, nullable=True)
#     number: Mapped[str] = mapped_column(String, nullable=True)
#     attributes: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
#
#     @declared_attr
#     @abc.abstractmethod
#     def record_associations(cls):
#         return relationship("RecordDistrictAssociation", back_populates="district")

