from typing import Annotated
from datetime import date

from sqlalchemy import String, Date, Integer
from sqlalchemy.orm import relationship, declared_attr, mapped_column, Mapped

from pydantic import Field as PydanticField

from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel, Base


class DataSource(ValidatorBaseModel):
    file: Annotated[str, PydanticField(..., description="Name of the file")]
    processed_date: Annotated[date, PydanticField(default=date.today(), description="Date the file was processed")]

    def __hash__(self):
        return hash(self.file)


class DataSourceModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    processed_date: Mapped[Date] = mapped_column(Date, nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, default=0)

    def __hash__(self):
        return hash(self.file)

    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='data_sources')
