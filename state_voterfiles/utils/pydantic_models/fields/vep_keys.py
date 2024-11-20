from sqlmodel import Field as SQLModelField, Relationship

from ..model_bases import SQLModelBase


class VEPMatch(SQLModelBase, table=True):
    __tablename__ = 'vep_match'
    id: int | None = SQLModelField(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
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
    records: 'RecordBaseModel' = Relationship(back_populates='vep_keys')

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