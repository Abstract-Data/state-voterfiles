from typing import Any, Dict, Optional, Annotated

from sqlmodel import Field as SQLModelField, JSON

from state_voterfiles.utils.pydantic_models.config import ValidatorConfig


class CustomFields(ValidatorConfig):
    fields: Dict[str, Any] | None = SQLModelField(default=None, sa_type=JSON)