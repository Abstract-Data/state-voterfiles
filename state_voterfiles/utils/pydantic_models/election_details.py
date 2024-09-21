from __future__ import annotations
from typing import Optional, Set, List, Annotated
from datetime import date
import hashlib

from pydantic import Field as PydanticField

from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
from state_voterfiles.utils.funcs.record_keygen import RecordKeyGenerator


generate_key = RecordKeyGenerator.generate_static_key


class ElectionTypeDetails(ValidatorConfig):
    id: str = PydanticField(default_factory=lambda: '')
    year: int
    election_type: str
    state: str
    city: Optional[str] = None
    county: Optional[str] = None
    dates: Optional[Set[date]] = PydanticField(default=None)
    desc: Optional[str] = None
    voted_records: Optional[List[VotedInElection]] = PydanticField(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, ElectionTypeDetails):
            return self.id == other.id
        return False

    def generate_hash_key(self) -> str:
        # Create a string with the essential properties of the election
        key_string = f"{self.year}_{self.election_type}_{self.state}"
        if self.city:
            key_string += f"_{self.city}"
        if self.county:
            key_string += f"_{self.county}"
        if self.dates:
            key_string += f"_{'_'.join(sorted(d.isoformat() for d in self.dates))}"

        # Generate a SHA256 hash of the key string
        return generate_key(key_string)  # Using first 16 characters for brevity

    def update(self, other: ElectionTypeDetails):
        if other.dates:
            self.dates.update(other.dates)
        if other.city and not self.city:
            self.city = other.city
        if other.county and not self.county:
            self.county = other.county


class VotedInElection(ValidatorConfig):
    id: Annotated[Optional[int], PydanticField(default=None)]
    year: Annotated[int, PydanticField(...)]
    party: Annotated[Optional[str], PydanticField(default=None)]
    vote_date: Annotated[Optional[date], PydanticField(default=None)]
    vote_method: Annotated[Optional[str], PydanticField(default=None)]
    election_id: Annotated[Optional[str], PydanticField(default=None)]
    record_vuid: Annotated[Optional[str], PydanticField(default=None)]
    record_id: Annotated[Optional[int], PydanticField(default=None)]
    record: Annotated[Optional['RecordBaseModel'], PydanticField(default=None)]
    election: Annotated[Optional[ElectionTypeDetails], PydanticField(default=None)]

    def __hash__(self):
        return hash((self.election_id, self.record_id, self.vote_date))


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
