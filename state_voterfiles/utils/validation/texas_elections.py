from __future__ import annotations
from typing import Type, Set
from datetime import datetime
import re

from pydantic_core import PydanticCustomError
from pydantic import Field as PydanticField
from pydantic.dataclasses import dataclass as pydantic_dataclass
from icecream import ic

from state_voterfiles.utils.db_models.fields.elections import VotedInElection, ElectionTypeDetails, RecordElectionVote
from state_voterfiles.utils.helpers.election_history_codes import (
    VoteMethodCodes,
    ElectionTypeCodes,
    PoliticalPartyCodes
)
import state_voterfiles.utils.validation.default_funcs as vfuncs
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig



@pydantic_dataclass
class TexasElectionHistoryValidator:
    @staticmethod
    def TEXAS(self) -> Type[ValidatorConfig]:
        election_settings = vfuncs.getattr_with_prefix("ELECTION", obj=self.data.settings)
        lists = vfuncs.dict_with_prefix("LISTS", dict_=self.data.settings)
        election_history = lists.get("election_types", None)
        voting_methods = lists.get("vote_methods", None)

        elections = {k: v for k, v in self.data.raw_data.items() if k.startswith(('PRI', 'GEN'))}
        election_detailed_list = set()
        election_list = []
        for e, v in elections.items():
            _d = {}
            if e.startswith((p := 'PRI', g := 'GEN')):
                try:
                    _year = datetime.strptime(f'20{e[-2:]}', '%Y').date()
                except ValueError:
                    raise PydanticCustomError(
                        'invalid_election_year',
                        f"Invalid election_year: {e[-2:]}"
                    )
                _d['year'] = f'{_year: %Y}'
                if e.startswith(p):
                    _d['election_type'] = ElectionTypeCodes.PRIMARY
                    if v.startswith('R'):
                        _d['party'] = PoliticalPartyCodes.REPUBLICAN
                    elif v.startswith('D'):
                        _d['party'] = PoliticalPartyCodes.DEMOCRATIC
                    else:
                        _d['party'] = PoliticalPartyCodes.INDEPENDENT

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

                _d['state'] = 'TX'
                e_details = ElectionTypeDetails(**_d)
                _d['election_id'] = e_details.id
                e_validator = VotedInElection(**_d)
                election_detailed_list.add(e_details)
                election_list.append(e_validator)
        for e in election_detailed_list:
            self.collected_elections.add(e)
        self.election_history = sorted(election_list, key=lambda x: x.year)
        return self

    @staticmethod
    def AUSTIN_TEXAS(self) -> ValidatorConfig:
        election_settings = self.data.settings.get('ELECTION', None)
        lists = election_settings.get('LISTS', None)
        election_history = lists.get("election_types", None)
        voting_methods = lists.get("vote_methods", None)
        _election_list = [
            k for k, v in self.data.raw_data.items()
            if k.startswith(tuple(election_history)) and k.endswith('VOTED') and v]

        elections = list(set(k.replace('VOTED', "").replace("PLACE", "").replace("PARTY", "") for k in _election_list))
        election_detailed_list = set()
        election_list = []
        for e in elections:
            info = {}
            e_data = {k: v for k, v in self.data.raw_data.items() if k.startswith(e)}
            if date_voted := e_data.get(f'{e}VOTED'):
                date_formats = ["%m/%d/%Y", "%Y%m%d"]
                for fmt in date_formats:
                    try:
                        _d = datetime.strptime(date_voted, fmt).date()
                        break
                    except ValueError:
                        continue
                info['vote_date'] = _d
                info['year'] = _d.year
            if info.get('vote_date'):
                if e.startswith('P'):
                    if e.startswith('PR'):
                        info['election_type'] = ElectionTypeCodes.PRIMARY_RUNOFF
                    else:
                        info['election_type'] = ElectionTypeCodes.PRIMARY
                elif e.startswith('G'):
                    if e.startswith('GR'):
                        info['election_type'] = ElectionTypeCodes.GENERAL_RUNOFF
                    elif e.startswith('GA'):
                        info['election_type'] = ElectionTypeCodes.GOVERNMENTAL_AUTHORITY
                    elif e.startswith('GL'):
                        info['election_type'] = ElectionTypeCodes.GOVERNMENT_LEGISLATIVE
                    else:
                        info['election_type'] = ElectionTypeCodes.GENERAL
                elif e.startswith('L'):
                    if e.startswith('LR'):
                        info['election_type'] = ElectionTypeCodes.LOCAL_RUNOFF
                    else:
                        info['election_type'] = ElectionTypeCodes.LOCAL
                elif e.startswith('SE'):
                    info['election_type'] = ElectionTypeCodes.SPECIAL
                elif e.startswith('CB'):
                    info['election_type'] = ElectionTypeCodes.CONGRESSIONAL
                else:
                    raise PydanticCustomError(
                        'invalid_election_type',
                        f"Invalid election type: {e}"
                    )
                if party := e_data.get(f'{e}PARTY'):
                    if party.startswith('REP'):
                        info['party'] = PoliticalPartyCodes.REPUBLICAN
                    elif party.startswith('DEM'):
                        info['party'] = PoliticalPartyCodes.DEMOCRATIC
                    else:
                        info['party'] = None
                info.setdefault('attributes', {}).update(
                    {
                        'city': 'Austin',
                        'file_election_code': e
                    }
                )
                info['state'] = 'TX'
                e_details = ElectionTypeDetails(**info)
                info['election_id'] = e_details.id
                election_detailed_list.add(e_details)
                e_obj = VotedInElection(**info)
                election_list.append(e_obj)
        self.election_history = sorted(election_list, key=lambda x: x.vote_date)
        self.collected_elections = election_detailed_list
        return self



    # @staticmethod
    # def PENNSYLVANIA(self) -> Type[ValidatorConfig]:

