from typing import Optional

from pydantic import Field as PydanticField
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig


class ValidatorBaseModel(ValidatorConfig):
    id: Optional[int] = PydanticField(default=None)