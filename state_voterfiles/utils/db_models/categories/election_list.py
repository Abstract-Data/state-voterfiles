from typing import Set, List

from pydantic import Field as PydanticField

from state_voterfiles.utils.abcs.validation_model_abcs import FileCategoryListABC
from state_voterfiles.utils.db_models.fields.elections import ElectionTypeDetails


class FileElectionList(FileCategoryListABC):
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
