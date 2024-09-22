from ..base import Base, mapped_column, Mapped
from sqlalchemy import String, Date, Integer
from sqlalchemy.orm import relationship, declared_attr


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
