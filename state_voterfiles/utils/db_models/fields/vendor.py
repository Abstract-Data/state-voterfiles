from typing import Dict, Any, Optional, Annotated

from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.dialects.postgresql import JSONB

from pydantic import Field as PydanticField

from state_voterfiles.utils.db_models.model_bases import Base, mapped_column, Mapped, ValidatorBaseModel
from state_voterfiles.utils.abcs.validation_model_abcs import RecordListABC
from state_voterfiles.utils.funcs import RecordKeyGenerator


class VendorName(RecordListABC):
    id: Optional[str] = PydanticField(default=None)
    name: Annotated[str, PydanticField(...)]

    def generate_hash_key(self) -> str:
        return RecordKeyGenerator.generate_static_key(self.name)


class VendorTags(ValidatorBaseModel):
    vendor_id: str = PydanticField(..., description="Name of the vendor")
    tags: Dict[str, Any] = PydanticField(..., description="List of tags associated with the vendor")


class VendorTagsModel(Base):
    __abstract__ = True

    vendor: Mapped[str] = mapped_column(String, nullable=False)
    tags: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    @declared_attr
    def record_id(self):
        return mapped_column(Integer, ForeignKey('record.id'), nullable=True)

    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='vendors')