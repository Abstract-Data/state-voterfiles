from __future__ import annotations

import abc

from pydantic import (
    Field,
    model_validator,
    AliasChoices,
    create_model,
)
from typing import Optional, Dict, Annotated, Type, Any, List, Union
import state_voterfiles.utils.validation.default_funcs as funcs
from state_voterfiles.utils.readers.toml_reader import TomlReader
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
from pathlib import Path
from state_voterfiles.utils.abcs.toml_record_fields_abc import (
    TomlFileFieldsABC
)


class RecordRenamer(ValidatorConfig, abc.ABC):
    person_dob: Annotated[Optional[str], Field(default=None)]
    person_dob_yearmonth: Annotated[Optional[str], Field(default=None)]
    person_dob_year: Annotated[Optional[str], Field(default=None)]
    person_dob_month: Annotated[Optional[str], Field(default=None)]
    person_dob_day: Annotated[Optional[str], Field(default=None)]
    voter_registration_date: Annotated[Optional[str], Field(default=None)]
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    date_format: Union[str, List[str]] = Field(...)
    settings: Dict[str, Any] = Field(default_factory=dict)
    pass


class VALIDATOR_FIELDS(TomlFileFieldsABC):

    @property
    def fields(self) -> Dict[str, str]:
        _field_toml = TomlReader(file=self._field_path, name=self._state.lower()).data
        self._fields = _field_toml
        return self._fields


def create_renamed_model(state: str, field_path: Path) -> Type[ValidatorConfig]:
    _fields = VALIDATOR_FIELDS(_state=state, _field_path=field_path)
    _not_null_fields = {k: k if v == "null" else v for k, v in _fields.FIELDS.items()}

    # _not_null_fields = {k: v for k, v in _fields.FIELDS.items() if v == "null"}  # Set fields that are not empty/null.
    _validators: Dict[str, Any] = {
        'clear_blank_strings': model_validator(mode='before')(funcs.clear_blank_strings),
        'create_raw_data_dict': model_validator(mode='before')(funcs.create_raw_data_dict),
    }  # Validators for the renaming model.

    # Create the field name dictionary for the model.
    _field_name_dict = {}
    for k, v in _not_null_fields.items():
        if isinstance(v, list):
            _field_name_dict[k] = (
                Annotated[
                    Optional[str],
                    Field(
                        default=None,
                        validation_alias=AliasChoices(*v)
                    )
                ]
            )
        else:
            _field_name_dict[k] = (
                Annotated[
                    Optional[str],
                    Field(
                        default=None,
                        validation_alias=AliasChoices(v)
                    )
                ]
            )

    # _field_name_dict = {
    #     k: (
    #         Annotated[
    #             Optional[str],
    #             Field(
    #                 default=None,
    #                 validation_alias=AliasChoices(*v if isinstance(v, list) else v)
    #             )
    #         ]
    #     ) for k, v in _not_null_fields.items()
    # }

    # Add the date format field to the model.
    _field_name_dict['date_format'] = (Union[str, List[str]], Field(default=_fields.FIELD_FORMATTING['date']))
    _field_name_dict['settings'] = (dict, Field(default=_fields.SETTINGS))

    # Add a field to store raw original data before transformation
    _field_name_dict['raw_data'] = (Dict[str, Any], Field(default_factory=dict))

    return create_model(
        'RecordRenamer',
        **_field_name_dict,
        __base__=RecordRenamer,
        __validators__=_validators
    )  # Create the model.
