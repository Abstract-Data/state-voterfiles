from typing import Optional, Dict, Any, Annotated

from pydantic.types import PastDate
from pydantic import Field as PydanticField
from sqlmodel import Field as SQLModelField, JSON

from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel
from state_voterfiles.utils.funcs import RecordKeyGenerator


class PersonName(ValidatorBaseModel):
    id: str | None = SQLModelField(default=None, primary_key=True)
    prefix: str | None = SQLModelField(default=None)
    first: str | None = SQLModelField(default=None)
    last: str | None = SQLModelField(default=None)
    middle: str | None = SQLModelField(default=None)
    suffix: str | None = SQLModelField(default=None)
    dob: PastDate | None = SQLModelField(default=None)
    gender: str | None = SQLModelField(default=None)
    other_fields: Dict[str, Any] | None = SQLModelField(sa_type=JSON, default=None)

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