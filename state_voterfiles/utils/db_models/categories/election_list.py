from typing import Set, List, Optional, Generator, Annotated

from sqlmodel import Field as SQLModelField
from pydantic import Field as PydanticField

from state_voterfiles.utils.abcs.validation_model_abcs import FileCategoryListABC
from state_voterfiles.utils.db_models.fields.elections import ElectionTypeDetails
from state_voterfiles.utils.funcs import RecordKeyGenerator


class FileElectionList(FileCategoryListABC):
    id: str | None = SQLModelField(default=None)
    elections: set[ElectionTypeDetails] = SQLModelField(default_factory=set)

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

    def generate_hash_key(self) -> str:
        return RecordKeyGenerator.generate_static_key("_".join([x.id for x in self.get_sorted_elections()]))

    def __iter__(self) -> Generator[ElectionTypeDetails, None, None]:
        for election in self.get_sorted_elections():
            yield election
