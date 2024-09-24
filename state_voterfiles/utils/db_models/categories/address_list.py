from typing import Optional, List, Set

from pydantic import Field as PydanticField

from state_voterfiles.utils.abcs.validation_model_abcs import RecordListABC, FileCategoryListABC
from state_voterfiles.utils.db_models.fields.address import Address
from state_voterfiles.utils.funcs import RecordKeyGenerator


class FileAddressList(FileCategoryListABC):
    addresses: Set[Address] = PydanticField(default_factory=set)

    def add_or_update(self, new_address: Address):
        for existing_address in self.addresses:
            if existing_address.id == new_address.id:
                existing_address.update(new_address)
                return
        self.addresses.add(new_address)
