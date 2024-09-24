from typing import Optional

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, registry
from sqlalchemy.sql import func
from sqlalchemy import DateTime, Integer

from pydantic import Field as PydanticField

from state_voterfiles.utils.pydantic_models.config import ValidatorConfig


mapper_registry = registry()

DeclarativeBase_ = declarative_base()


class ValidatorBaseModel(ValidatorConfig):
    id: Optional[int] = PydanticField(default=None)


class Base(DeclarativeBase_):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    registry = mapper_registry
    metadata = mapper_registry.metadata
