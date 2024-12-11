from typing import Type
from datetime import datetime

from pydantic_core import PydanticCustomError
from pydantic.dataclasses import dataclass as pydantic_dataclass

from . import default_funcs as vfuncs
from ..pydantic_models.config import ValidatorConfig
from election_utils.election_models import ElectionVote, ElectionVoteMethod, ElectionTypeDetails, ElectionDataTuple
from election_utils.election_history_codes import (
    VoteMethodCodesBase,
    ElectionTypeCodesBase,
    PoliticalPartyCodesBase
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
                    _d['election_type'] = ElectionTypeCodesBase.PRIMARY
                    if v: 
                        if v.startswith('R'):
                            _d['political_party'] = PoliticalPartyCodesBase.REPUBLICAN
                        elif v.startswith('D'):
                            _d['political_party'] = PoliticalPartyCodesBase.DEMOCRATIC
                elif e.startswith(g):
                    _d['election_type'] = ElectionTypeCodesBase.GENERAL
                else:
                    raise PydanticCustomError(
                        'invalid_election_type',
                        f"Invalid election type: {e}"
                    )
                if v:
                    if v.endswith('E'):
                        _d['vote_method'] = VoteMethodCodesBase.EARLY_VOTE
                    elif v.endswith('A'):
                        _d['vote_method'] = VoteMethodCodesBase.ABSENTEE
                    elif len(v) == 1:
                        _d['vote_method'] = VoteMethodCodesBase.IN_PERSON
                    else:
                        _d['vote_method'] = None
                    e_validator = ElectionVote(**_d)
                election_list.append(e_validator)

        self.elections = election_list
        return self
