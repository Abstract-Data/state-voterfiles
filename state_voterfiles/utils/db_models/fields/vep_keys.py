from ..base import Base, mapped_column, Mapped
from typing import Optional
from sqlalchemy import String, Boolean
from sqlalchemy.orm import relationship, declared_attr


class VEPKeysModel(Base):
    __abstract__ = True

    uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    long: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    short: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    name_dob: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    addr_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    addr_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_key_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    best_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    uses_mailzip: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # @abstract_declared_attr
    # def record_id(cls):
    #     return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=True)
    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='vep_keys')