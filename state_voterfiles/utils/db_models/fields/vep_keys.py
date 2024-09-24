from typing import Optional, Annotated
from sqlalchemy import String, Boolean
from sqlalchemy.orm import relationship, declared_attr, mapped_column, Mapped

from pydantic import Field as PydanticField

from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel, Base


class VEPMatch(ValidatorBaseModel):
    uuid: Annotated[
        Optional[str],
        PydanticField(default=None),
    ]
    long: Annotated[
        Optional[str],
        PydanticField(default=None),
    ]
    short: Annotated[
        Optional[str],
        PydanticField(default=None),
    ]
    name_dob: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    addr_text: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    addr_key: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    full_key: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    full_key_hash: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    best_key: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    uses_mailzip: Annotated[
        Optional[bool],
        PydanticField(default=None)
    ]


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