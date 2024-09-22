from ..base import Base, mapped_column, Mapped
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship, declared_attr


class RecordDistrictModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(ForeignKey('districts.id'), nullable=False)

    district: Mapped['DistrictModel'] = relationship("District", back_populates="record_associations")

    @declared_attr
    def record_id(cls):
        return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=False)

    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='government_districts')
