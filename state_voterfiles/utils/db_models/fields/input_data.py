from ..base import Base, mapped_column, Mapped
from typing import Dict, Any, List
from sqlalchemy import JSON
from sqlalchemy.orm import relationship, declared_attr


class InputDataModel(Base):
    __abstract__ = True

    original_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    renamed_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    corrections: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    date_format: Mapped[List[str]] = mapped_column(JSON, nullable=False)

    # @abstract_declared_attr
    # def record_id(cls):
    #     return mapped_column(Integer, ForeignKey('record.id'), nullable=True)
    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='input_data')
