from typing import Type
from datetime import datetime

from pydantic_core import PydanticCustomError
from pydantic.dataclasses import dataclass as pydantic_dataclass

import state_voterfiles.utils.validation.default_funcs as vfuncs
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
import state_voterfiles.utils.db_models.fields.elections as election_fields
from state_voterfiles.utils.helpers.election_history_codes import (
    VoteMethodCodes,
    ElectionTypeCodes,
    PoliticalPartyCodes
)


@pydantic_dataclass
class StateElectionHistoryValidator:
    @staticmethod
    def TEXAS(self) -> Type[ValidatorConfig]:

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
                    _d['vote_method'] = VoteMethodCodes.EARLY_VOTE
                elif v.endswith('A'):
                    _d['vote_method'] = VoteMethodCodes.ABSENTEE
                elif len(v) == 1:
                    _d['vote_method'] = VoteMethodCodes.IN_PERSON
                else:
                    _d['vote_method'] = None
                e_validator = election_fields.VotedInElection(**_d)
                election_list.append(e_validator)

        # self.elections = election_list
        return self
