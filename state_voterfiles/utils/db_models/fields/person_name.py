from typing import Dict, Any, Optional
from datetime import datetime

from sqlmodel import Field as SQLModelField, JSON, Relationship, Column, DateTime, func, Date, text
from pydantic.types import PastDate
from sqlalchemy.dialects.postgresql import TIMESTAMP


from state_voterfiles.utils.funcs.record_keygen import RecordKeyGenerator
from state_voterfiles.utils.db_models.model_bases import SQLModelBase


class PersonName(SQLModelBase, table=True):
    __tablename__ = 'person_name'
    id: Optional[str] = SQLModelField(default=None, primary_key=True)
    prefix: Optional[str] = SQLModelField(default=None)
    first: Optional[str] = SQLModelField(default=None)
    last: Optional[str] = SQLModelField(default=None)
    middle: Optional[str] = SQLModelField(default=None)
    suffix: Optional[str] = SQLModelField(default=None)
    dob: Optional[PastDate] = SQLModelField(default=None, sa_type=Date)
    gender: Optional[str] = SQLModelField(default=None)
    other_fields: Optional[Dict[str, Any]] = SQLModelField(sa_type=JSON, default=None, nullable=True)
    created_at: datetime = SQLModelField(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP")
        )
    )
    updated_at: datetime = SQLModelField(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        ),
        default=None
    )
    records: list['RecordBaseModel'] = Relationship(back_populates='name')

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def generate_hash_key(self) -> str:
        keys = [self.prefix, self.first, self.middle, self.last,  self.suffix, self.dob,]
        return RecordKeyGenerator.generate_static_key("_".join([str(key) for key in keys if key is not None]))
# class PersonNameModel(Base):
#     __abstract__ = True
#
#     prefix: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     first: Mapped[str] = mapped_column(String, nullable=False)
#     last: Mapped[str] = mapped_column(String, nullable=False)
#     middle: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     suffix: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
#     gender: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
#     other_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
#
#     # @abstract_declared_attr
#     # def record_id(cls):
#     #     return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def record(cls):
#         return relationship('RecordModel', back_populates='name')