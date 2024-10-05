from __future__ import annotations
from typing import Dict, Any, List, Annotated, Optional

from pydantic import Field as PydanticField

from sqlmodel import Field as SQLModelField, JSON
from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel


class InputData(ValidatorBaseModel):
    input_data: Dict[str, Any] | None = SQLModelField(sa_type=JSON, default=None)
    original_data: Dict[str, Any] | None = SQLModelField(sa_type=JSON, default=None)
    renamed_data: Dict[str, Any] | None = SQLModelField(sa_type=JSON, default=None)
    corrections: Dict[str, Any] | None = SQLModelField(sa_type=JSON, default=None)
    settings: Dict[str, Any] | None = SQLModelField(sa_type=JSON, default=None)
    date_format: Dict[str, Any] | str | None = SQLModelField(sa_type=JSON, default=None)


# class InputDataModel(Base):
#     __abstract__ = True
#
#     original_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
#     renamed_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
#     corrections: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
#     settings: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
#     date_format: Mapped[List[str]] = mapped_column(JSON, nullable=False)
#
#     @declared_attr
#     @abc.abstractmethod
#     def record_id(cls):
#         return mapped_column(String, ForeignKey('record.id'), nullable=True)
#     @declared_attr
#     @abc.abstractmethod
#     def record(cls):
#         return relationship('RecordModel', back_populates='input_data')
