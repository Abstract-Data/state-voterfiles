from ..base import Base, mapped_column, Mapped
from typing import Dict, Any
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.dialects.postgresql import JSONB


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