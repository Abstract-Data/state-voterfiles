from typing import Optional, Dict, Any, Annotated
from datetime import date
from sqlalchemy import String, JSON, Date
from sqlalchemy.orm import relationship, declared_attr, mapped_column, Mapped

from pydantic import Field as PydanticField

from state_voterfiles.utils.db_models.model_bases import ValidatorBaseModel, Base


class VoterRegistration(ValidatorBaseModel):
    vuid: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    edr: Annotated[
        Optional[date],
        PydanticField(default=None),
    ]
    status: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    county: Annotated[
        Optional[str],
        PydanticField(default=None)
    ]
    attributes: Annotated[
        Optional[Dict[str, Any]],
        PydanticField(default=None)
    ]


class VoterRegistrationModel(Base):
    __abstract__ = True

    vuid: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True)
    edr: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    county: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # @abstract_declared_attr
    # def record_id(cls):
    #     return mapped_column(Integer, ForeignKey('RecordModel.id'), nullable=True)

    @declared_attr
    def record(cls):
        return relationship('RecordModel', back_populates='voter_registration')