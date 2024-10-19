import abc
from sqlmodel import SQLModel
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
from pydantic import ConfigDict


class ValidatorBaseModel(ValidatorConfig):
    pass


class SQLModelBase(SQLModel, abc.ABC):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        arbitrary_types_allowed=True
    )
