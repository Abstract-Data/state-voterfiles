from typing import Optional, Annotated

from sqlmodel import Field as SQLModelField
from pydantic import Field as PydanticField

from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel


class VEPMatch(ValidatorBaseModel):
    uuid: str | None = SQLModelField(default=None)
    long: str | None = SQLModelField(default=None)
    short: str | None = SQLModelField(default=None)
    name_dob: str | None = SQLModelField(default=None)
    addr_text: str | None = SQLModelField(default=None)
    addr_key: str | None = SQLModelField(default=None)
    full_key: str | None = SQLModelField(default=None)
    full_key_hash: str | None = SQLModelField(default=None)
    best_key: str | None = SQLModelField(default=None)
    uses_mailzip: bool | None = SQLModelField(default=None)


# class VEPKeysModel(Base):
#     __abstract__ = True
#
#     uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     long: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     short: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     name_dob: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     addr_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     addr_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     full_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     full_key_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     best_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     uses_mailzip: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
#
#     # @abstract_declared_attr
#     # def record_id(cls):
#     #     return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=True)
#     @declared_attr
#     @abc.abstractmethod
#     def record(cls):
#         return relationship('RecordModel', back_populates='vep_keys')