from typing import Any, Dict, Optional, Annotated

from pydantic import Field as PydanticField

from state_voterfiles.utils.pydantic_models.config import ValidatorConfig


class CustomFields(ValidatorConfig):
    fields: Annotated[
        Optional[Dict[str, Any]],
        PydanticField(
            default=None,
        )
    ]