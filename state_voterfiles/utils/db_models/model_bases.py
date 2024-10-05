from typing import Optional, Any, Type, Dict, Tuple, TypeVar, Annotated
import abc

# from django.db import models
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType
from pydantic import Field as PydanticField
from sqlmodel import Field as SQLModelField

from state_voterfiles.utils.pydantic_models.config import ValidatorConfig


#
#
# T = TypeVar('T', bound='Base')
#
# mapper_registry = registry()


class ValidatorBaseModel(ValidatorConfig):
    id: int | None = SQLModelField(default=None)

#
# class AbstractBaseMeta(type(models.Model), abc.ABCMeta):
#     pass

#
# class AbstractModelBase(models.Model, abc.ABC, metaclass=AbstractBaseMeta):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#
#     class Meta:
#         abstract = True
#         indexes = [
#             models.Index(fields=['content_type', 'object_id']),
#         ]

# class AbstractBaseMeta(type(DeclarativeBase), abc.ABCMeta):
#     pass
#
#
# class AbstractBase(DeclarativeBase, abc.ABC, metaclass=AbstractBaseMeta):
#     __abstract__ = True
#
#     created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
#     updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
#     registry = mapper_registry
#     metadata = mapper_registry.metadata
#
#     @classmethod
#     @abc.abstractmethod
#     def add_or_update(cls, session, data):
#         pass
#
#     @abc.abstractmethod
#     def to_dict(self):
#         pass
#
#
# class Base(AbstractBase):
#     __abstract__ = True
#     __table_args__ = {'extend_existing': True}
#     id: Mapped[str] = mapped_column(String, primary_key=True)
#
#     def to_dict(self):
#         return {c.name: getattr(self, c.name) for c in self.__table__.columns}
#
#     def _update_attribute(self, key: str, new_value: Any) -> bool:
#         if hasattr(self, key):
#             current_value = getattr(self, key)
#
#             if current_value != new_value:
#                 if isinstance(current_value, set) and isinstance(new_value, (set, list)):
#                     setattr(self, key, current_value.union(set(new_value)))
#                 elif isinstance(current_value, list) and isinstance(new_value, list):
#                     current_value.extend([item for item in new_value if item not in current_value])
#                 elif isinstance(current_value, dict) and isinstance(new_value, dict):
#                     current_value.update(new_value)
#                 else:
#                     setattr(self, key, new_value)
#                 return True
#         elif not key.startswith('_'):  # Avoid setting private attributes
#             setattr(self, key, new_value)
#             return True
#         return False
#
#     def update_from_dict(self, data: Dict[str, Any]) -> bool:
#         updated = False
#         for key, value in data.items():
#             if self._update_attribute(key, value):
#                 updated = True
#         return updated
#
#     @classmethod
#     def add_or_update(cls: Type[T], session: Session, data: Dict[str, Any]) -> Tuple[T, bool]:
#         primary_keys = inspect(cls).primary_key
#         filter_condition = {pk.name: data.get(pk.name) for pk in primary_keys if pk.name in data}
#
#         if len(filter_condition) != len(primary_keys):
#             raise ValueError("All primary key values must be provided for add_or_update operation")
#
#         instance = session.query(cls).filter_by(**filter_condition).first()
#
#         if instance:
#             updated = instance.update_from_dict(data)
#         else:
#             instance = cls(**data)
#             session.add(instance)
#             updated = True
#
#         return instance, updated
#
#     @hybrid_property
#     def searchable_fields(self):
#         return {c.name: getattr(self, c.name) for c in self.__table__.columns
#                 if not c.primary_key and c.name not in ['created_at', 'updated_at']}
#
#     @classmethod
#     def get_column_names(cls):
#         return [c.name for c in cls.__table__.columns]
