from typing import Set, Optional

from sqlmodel import Field as SQLModelField, JSON, SQLModel, Relationship as SQLModelRelationship

from state_voterfiles.utils.abcs.validation_model_abcs import FileCategoryListABC
from state_voterfiles.utils.db_models.fields.district import District
from state_voterfiles.utils.funcs import RecordKeyGenerator


class FileDistrictList(FileCategoryListABC):
    id: str | None = SQLModelField(default=None, primary_key=True)
    districts: set["District"] = SQLModelField(default_factory=set, sa_type=JSON)

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def add_or_update(self, new_district: District):
        for existing_district in self.districts:
            if existing_district.id == new_district.id:
                if existing_district.attributes != new_district.attributes:
                    existing_district.update(new_district)
                return
        self.districts.add(new_district)

    def generate_hash_key(self) -> str:
        return RecordKeyGenerator.generate_static_key(
            "_".join(
                sorted(
                    [str(district.id) for district in self.districts]
                )
            )
        )
