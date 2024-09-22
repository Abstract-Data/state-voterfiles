from __future__ import annotations
from typing import Annotated, Optional, Dict, Any, List, ClassVar, Set
from datetime import date

from pydantic import Field as PydanticField

from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
from state_voterfiles.utils.funcs.record_keygen import RecordKeyGenerator
from state_voterfiles.utils.pydantic_models.base import ValidatorBaseModel
from state_voterfiles.utils.pydantic_models.field_models import Address, District, ValidatedPhoneNumber
from state_voterfiles.utils.pydantic_models.election_details import ElectionTypeDetails

generate_key = RecordKeyGenerator.generate_static_key

# TODO: Build a FileData class to store the SETS of data for each file (Elections, Addresses, Phone Numbers, etc.)
# TODO: Rework validation processs to use the FileData class to store the data for each file
# TODO: Incorporate the FileType RecordsLists into the PreValidationCleanUp process
# TODO: Build a database upload process for SQLAlchemy based off of the keys in the FileData class and records.


class RecordAddressList(ValidatorBaseModel):
    id: str = PydanticField(default_factory=lambda: '')
    residential_id: Optional[str] = PydanticField(default_factory=lambda: '')
    mailing_id: Optional[str] = PydanticField(default_factory=lambda: '')

    addresses: Optional[List[Address]] = PydanticField(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, RecordAddressList):
            return self.id == other.id
        return False

    def generate_hash_key(self) -> str:
        # Create a string with the essential properties of the election
        if all(_keys := [self.residential_id, self.mailing_id]):
            key_string = f"{self.residential_id}_{self.mailing_id}"
        elif any(_keys):
            key_string = f"{next((_key for _key in _keys if _key))}"
        else:
            raise ValueError("No address keys found")

        # Generate a SHA256 hash of the key string
        return generate_key(key_string)


class RecordDistrictList(ValidatorBaseModel):
    id: str = PydanticField(default_factory=lambda: '')
    districts: Annotated[List[District], PydanticField(default_factory=list)]

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, RecordDistrictList):
            return self.id == other.id
        return False

    def generate_hash_key(self) -> str:
        # Create a string with the essential properties of the election
        key_string = f"{'_'.join(sorted(d.id for d in self.districts))}"

        # Generate a SHA256 hash of the key string
        return generate_key(key_string)


class RecordPhoneNumberList(ValidatorBaseModel):
    id: str = PydanticField(default_factory=lambda: '')
    phone_numbers: Annotated[List[ValidatedPhoneNumber], PydanticField(default_factory=list)]

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, RecordPhoneNumberList):
            return self.id == other.id
        return False

    def generate_hash_key(self) -> str:
        # Create a string with the essential properties of the election
        key_string = f"{'_'.join(sorted(p.phone for p in self.phone_numbers))}"

        # Generate a SHA256 hash of the key string
        return generate_key(key_string)


class RecordVendorList(ValidatorBaseModel):
    id: str = PydanticField(default_factory=lambda: '')
    vendors: Annotated[List[str], PydanticField(default_factory=list)]

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, RecordVendorList):
            return self.id == other.id
        return False

    def generate_hash_key(self) -> str:
        # Create a string with the essential properties of the election
        key_string = f"{'_'.join(sorted(v for v in self.vendors))}"

        # Generate a SHA256 hash of the key string
        return generate_key(key_string)


class ElectionList(ValidatorConfig):
    elections: Set[ElectionTypeDetails] = PydanticField(default_factory=set)

    def add_or_update(self, new_election: ElectionTypeDetails):
        for existing_election in self.elections:
            if (existing_election.year == new_election.year and
                    existing_election.election_type == new_election.election_type and
                    existing_election.state == new_election.state):
                existing_election.update(new_election)
                return
        self.elections.add(new_election)

    def get_sorted_elections(self) -> List[ElectionTypeDetails]:
        return sorted(self.elections, key=lambda x: x.year if not x.dates else min(x.dates))

    def __iter__(self):
        return iter(self.get_sorted_elections())
