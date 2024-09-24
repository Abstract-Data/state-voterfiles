from __future__ import annotations
from typing import Dict, Any, List, Annotated, Optional

from sqlalchemy import JSON
from sqlalchemy.orm import relationship, declared_attr, mapped_column, Mapped

from pydantic import Field as PydanticField

from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel, Base


class InputData(ValidatorBaseModel):
    input_data: Annotated[Optional[Dict[str, Any]], PydanticField(default=None)]
    original_data: Annotated[Optional[Dict[str, Any]], PydanticField(default=None)]
    renamed_data: Annotated[Optional[Dict[str, Any]], PydanticField(default=None)]
    corrections: Annotated[Optional[Dict[str, Any]], PydanticField(default=None)]
    settings: Annotated[Optional[Dict[str, Any]], PydanticField(default=None)]
    date_format: Annotated[Optional[str | List[str]], PydanticField(default=None)]


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
