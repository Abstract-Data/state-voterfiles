from typing import Annotated, Optional
from datetime import date

from pydantic import Field as PydanticField
from sqlmodel import Field as SQLModelField

from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel


class DataSource(ValidatorBaseModel):
    file: str = SQLModelField(..., description="Name of the file")
    processed_date: date | None = SQLModelField(default=None, description="Date the file was processed")

    def __hash__(self):
        return hash(self.file)


# class DataSourceModel(Base):
#     __abstract__ = True
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     file: Mapped[str] = mapped_column(String, nullable=False, unique=True)
#     processed_date: Mapped[Date] = mapped_column(Date, nullable=False)
#     record_count: Mapped[int] = mapped_column(Integer, default=0)
#
#     def __hash__(self):
#         return hash(self.file)
#
#     @declared_attr
#     @abc.abstractmethod
#     def record(cls):
#         return relationship('RecordModel', back_populates='data_sources')
