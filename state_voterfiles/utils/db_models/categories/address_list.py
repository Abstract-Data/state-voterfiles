from typing import Set, Annotated

from pydantic import Field as PydanticField
from sqlmodel import Field as SQLModelField

from state_voterfiles.utils.abcs.validation_model_abcs import FileCategoryListABC
from state_voterfiles.utils.db_models.fields.address import Address
from state_voterfiles.utils.funcs import RecordKeyGenerator


class FileAddressList(FileCategoryListABC):
    addresses: set[Address] = SQLModelField(default_factory=set)

    def add_or_update(self, new_address: Address):
        for existing_address in self.addresses:
            if existing_address.id == new_address.id:
                existing_address.update(new_address)
                return
        self.addresses.add(new_address)

    def generate_hash_key(self) -> str:
        self.id = RecordKeyGenerator.generate_static_key(
            "_".join(
                sorted(
                    [str(address.id) for address in self.addresses]
                )
            )
        )
        return self.id
