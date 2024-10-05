from typing import Optional, Dict, Any, Annotated
from datetime import date

from sqlmodel import Field as SQLModelField, JSON
from pydantic import Field as PydanticField

from state_voterfiles.utils.funcs import RecordKeyGenerator
from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel


class VoterRegistration(ValidatorBaseModel):
    id: str | None = SQLModelField(default=None, primary_key=True)
    vuid: str | None = SQLModelField(default=None)
    edr: date | None = SQLModelField(default=None)
    status: str | None = SQLModelField(default=None)
    county: str | None = SQLModelField(default=None)
    attributes: Dict[str, Any] | None = SQLModelField(default=None, sa_type=JSON)

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.vuid)

    def __eq__(self, other):
        return self.vuid == other.vuid

    def generate_hash_key(self) -> str:
        return RecordKeyGenerator.generate_static_key(str(self.vuid))

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self


# class VoterRegistrationModel(Base):
#     __abstract__ = True
#
#     vuid: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True)
#     edr: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
#     status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     county: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
#
#     # @abstract_declared_attr
#     # def record_id(cls):
#     #     return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=True)
#
#     @declared_attr
#     @abc.abstractmethod
#     def record(cls):
#         return relationship('RecordModel', back_populates='voter_registration')
