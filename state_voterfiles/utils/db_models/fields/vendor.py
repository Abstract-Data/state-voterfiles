from __future__ import annotations
from typing import Dict, Any, Optional, Annotated

from sqlmodel import Field as SQLModelField
from pydantic import Field as PydanticField

from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel
from state_voterfiles.utils.abcs.validation_model_abcs import RecordListABC
from state_voterfiles.utils.funcs import RecordKeyGenerator


class VendorName(RecordListABC):
    id: str | None = SQLModelField(default=None)
    name: str = SQLModelField(...)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def generate_hash_key(self) -> str:
        return RecordKeyGenerator.generate_static_key(self.name)

    def update(self, new_record: VendorName):
        self.name = new_record.name


class VendorTags(ValidatorBaseModel):
    vendor_id: str = SQLModelField(..., description="Name of the vendor")
    tags: Dict[str, Any] = SQLModelField(..., description="List of tags associated with the vendor")


# class VendorNameModel(Base):
#     __abstract__ = True
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String, nullable=False)
#
#
# class VendorTagsModel(Base):
#     __abstract__ = True
#
#     tags: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
#
#     @declared_attr
#     @abc.abstractmethod
#     def vendor_id(cls):
#         return mapped_column(Integer, ForeignKey('vendor_name.id'), nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def record_id(self):
#         return mapped_column(Integer, ForeignKey('record.id'), nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def record(cls):
#         return relationship('RecordModel', back_populates='vendors')

