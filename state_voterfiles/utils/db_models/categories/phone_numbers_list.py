from __future__ import annotations
from typing import Set, Annotated

from sqlmodel import Field as SQLModelField
from pydantic import Field as PydanticField

from state_voterfiles.utils.abcs.validation_model_abcs import FileCategoryListABC
from state_voterfiles.utils.db_models.fields.phone_number import ValidatedPhoneNumber


class FilePhoneNumberList(FileCategoryListABC):
    phone_numbers: set['ValidatedPhoneNumber'] = SQLModelField(default_factory=set)

    def add_or_update(self, new_phone_number: 'ValidatedPhoneNumber'):
        for existing_phone_number in self.phone_numbers:
            if existing_phone_number.id == new_phone_number.id:
                existing_phone_number.update(new_phone_number)
                return
        self.phone_numbers.add(new_phone_number)

    def generate_hash_key(self) -> str:
        return "_".join(sorted([x.id for x in self.phone_numbers]))