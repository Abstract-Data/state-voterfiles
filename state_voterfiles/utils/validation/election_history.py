from __future__ import annotations
from typing import Type
from datetime import datetime
from state_voterfiles.utils.pydantic_models.field_models import Election
from state_voterfiles.utils.validation.election_history_codes import (
    VoteMethodCodes, ElectionTypeCodes, PoliticalPartyCodes
)
import state_voterfiles.utils.validation.default_funcs as vfuncs
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
from pydantic_core import PydanticCustomError
from pydantic.dataclasses import dataclass as pydantic_dataclass


@pydantic_dataclass
class StateElectionHistoryValidator:
    @staticmethod
    def TEXAS(self) -> Type[ValidatorConfig]:
        election_settings = vfuncs.getattr_with_prefix("ELECTION", obj=self.data.settings)
        lists = vfuncs.dict_with_prefix("LISTS", dict_=self.data.settings)
        election_history = lists.get("election_types", None)
        voting_methods = lists.get("vote_methods", None)

        elections = {k: v for k, v in self.data.raw_data.items() if k.startswith(('PRI', 'GEN'))}
        election_list = []
        for e, v in elections.items():
            _d = {}
            if e.startswith((p := 'PRI', g := 'GEN')):
                try:
                    _year = datetime.strptime(f'20{e[-2:]}', '%Y')
                except ValueError:
                    raise PydanticCustomError(
                        'invalid_election_year',
                        f"Invalid election_year: {e[-2:]}"
                    )
                _d['year'] = f'{_year: %Y}'
                if e.startswith(p):
                    _d['election_type'] = ElectionTypeCodes.PRIMARY
                    if v.startswith('R'):
                        _d['political_party'] = PoliticalPartyCodes.REPUBLICAN
                    elif v.startswith('D'):
                        _d['political_party'] = PoliticalPartyCodes.DEMOCRATIC
                elif e.startswith(g):
                    _d['election_type'] = ElectionTypeCodes.GENERAL
                else:
                    raise PydanticCustomError(
                        'invalid_election_type',
                        f"Invalid election type: {e}"
                    )

                if v.endswith('E'):
                    _d['vote_method'] = VoteMethodCodes.EARLY_VOTING
                elif v.endswith('A'):
                    _d['vote_method'] = VoteMethodCodes.ABSENTEE
                else:
                    _d['vote_method'] = VoteMethodCodes.IN_PERSON
                e_validator = Election(**_d)
                election_list.append(e_validator)

        self.election_history = election_list
        return self
