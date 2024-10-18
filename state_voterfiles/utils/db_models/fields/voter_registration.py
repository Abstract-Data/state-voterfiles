from typing import Dict, Any
from datetime import date, datetime

from sqlmodel import Field as SQLModelField, JSON, Relationship, Column, DateTime, func

from state_voterfiles.utils.funcs.record_keygen import RecordKeyGenerator
from state_voterfiles.utils.db_models.model_bases import SQLModelBase
# from state_voterfiles.utils.db_models.fields.elections import VoterAndElectionLink


class VoterRegistration(SQLModelBase, table=True):
    __tablename__ = 'voter_registration'
    id: str | None = SQLModelField(default=None, primary_key=True)
    vuid: str | None = SQLModelField(default=None, unique=True)
    edr: date | None = SQLModelField(default=None)
    status: str | None = SQLModelField(default=None)
    county: str | None = SQLModelField(default=None)
    precinct_number: str | None = SQLModelField(default=None)
    precinct_name: str | None = SQLModelField(default=None)
    attributes: Dict[str, Any] | None = SQLModelField(default=None, sa_type=JSON)
    created_at: datetime = SQLModelField(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        default=None
    )
    updated_at: datetime = SQLModelField(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        ),
        default=None
    )
    # vote_history: list["VotedInElection"] = Relationship(
    #     back_populates="voters",
    #     link_model=VoterAndElectionLink,
    #     sa_relationship_kwargs={
    #         'primaryjoin': 'VoterRegistration.vuid == VoterAndElectionLink.voter_id',
    #         'secondaryjoin': 'VoterAndElectionLink.vote_history_id == VotedInElection.id',
    #         'overlaps': "records,voters"
    #     }
    # )
    records: list["RecordBaseModel"] = Relationship(back_populates="voter_registration")

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
