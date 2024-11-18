from typing import Type, List
from datetime import datetime
import re

from pydantic_core import PydanticCustomError
from pydantic import Field as PydanticField
from pydantic.dataclasses import dataclass as pydantic_dataclass
from icecream import ic

import state_voterfiles.utils.validation.default_funcs as vfuncs
from election_utils.election_models import ElectionVoteMethod, ElectionTypeDetails, ElectionVote, ElectionDataTuple
from election_utils.election_history_codes import (
    VoteMethodCodesBase,
    ElectionTypeCodesBase,
    PoliticalPartyCodesBase
)
from ..pydantic_models.config import ValidatorConfig


@pydantic_dataclass
class TexasElectionHistoryValidator:
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
                    _year = datetime.strptime(f'20{e[-2:]}', '%Y').date()
                except ValueError:
                    raise PydanticCustomError(
                        'invalid_election_year',
                        f"Invalid election_year: {e[-2:]}"
                    )
                _d['year'] = f'{_year: %Y}'
                if e.startswith(p):
                    _d['election_type'] = ElectionTypeCodesBase.PRIMARY
                    if v.startswith('R'):
                        _d['party'] = PoliticalPartyCodesBase.REPUBLICAN
                    elif v.startswith('D'):
                        _d['party'] = PoliticalPartyCodesBase.DEMOCRATIC
                    else:
                        _d['party'] = PoliticalPartyCodesBase.INDEPENDENT

                elif e.startswith(g):
                    _d['election_type'] = ElectionTypeCodesBase.GENERAL
                else:
                    raise PydanticCustomError(
                        'invalid_election_type',
                        f"Invalid election type: {e}"
                    )

                if v.endswith('E'):
                    _d['vote_method'] = VoteMethodCodesBase.EARLY_VOTE
                elif v.endswith('A'):
                    _d['vote_method'] = VoteMethodCodesBase.ABSENTEE
                elif v.endswith(('V', 'D', ''R'')):
                    _d['vote_method'] = VoteMethodCodesBase.IN_PERSON
                else:
                    _d['vote_method'] = None

                _d['state'] = 'TX'
                e_details = ElectionTypeDetails(**_d)
                e_vote_method = ElectionVoteMethod(election_id=e_details.id, **_d)
                e_voter_record = ElectionVote(
                    election_id=e_details.id,
                    vote_method_id=e_vote_method.id,
                )
                election_list.append(
                    ElectionDataTuple(
                        election=e_details,
                        vote_method=e_vote_method,
                        vote_record=e_voter_record
                    )
                )
        self.elections = election_list
        return self

    # @staticmethod
    # def AUSTIN_TEXAS(self) -> ValidatorConfig:
    #     election_settings = self.data.settings.get('ELECTION', None)
    #     lists = election_settings.get('LISTS', None)
    #     election_history = lists.get("election_types", None)
    #     voting_methods = lists.get("vote_methods", None)
    #     _election_list = [
    #         k for k, v in self.data.raw_data.items()
    #         if k.startswith(tuple(election_history)) and k.endswith('VOTED') and v]
    #
    #     elections = list(set(k.replace('VOTED', "").replace("PLACE", "").replace("PARTY", "") for k in _election_list))
    #     election_detailed_list = set()
    #     election_list = []
    #     for e in elections:
    #         info = {}
    #         e_data = {k: v for k, v in self.data.raw_data.items() if k.startswith(e)}
    #         if date_voted := e_data.get(f'{e}VOTED'):
    #             date_formats = ["%m/%d/%Y", "%Y%m%d"]
    #             for fmt in date_formats:
    #                 try:
    #                     _d = datetime.strptime(date_voted, fmt).date()
    #                     break
    #                 except ValueError:
    #                     continue
    #             info['vote_date'] = _d
    #             info['year'] = _d.year
    #         if info.get('vote_date'):
    #             if e.startswith('P'):
    #                 if e.startswith('PR'):
    #                     info['election_type'] = ElectionTypeCodesBase.PRIMARY_RUNOFF
    #                 else:
    #                     info['election_type'] = ElectionTypeCodesBase.PRIMARY
    #             elif e.startswith('G'):
    #                 if e.startswith('GR'):
    #                     info['election_type'] = ElectionTypeCodesBase.GENERAL_RUNOFF
    #                 elif e.startswith('GA'):
    #                     info['election_type'] = ElectionTypeCodesBase.GOVERNMENTAL_AUTHORITY
    #                 elif e.startswith('GL'):
    #                     info['election_type'] = ElectionTypeCodesBase.GOVERNMENT_LEGISLATIVE
    #                 else:
    #                     info['election_type'] = ElectionTypeCodesBase.GENERAL
    #             elif e.startswith('L'):
    #                 if e.startswith('LR'):
    #                     info['election_type'] = ElectionTypeCodesBase.LOCAL_RUNOFF
    #                 else:
    #                     info['election_type'] = ElectionTypeCodesBase.LOCAL
    #             elif e.startswith('SE'):
    #                 info['election_type'] = ElectionTypeCodesBase.SPECIAL
    #             elif e.startswith('CB'):
    #                 info['election_type'] = ElectionTypeCodesBase.CONGRESSIONAL
    #             else:
    #                 raise PydanticCustomError(
    #                     'invalid_election_type',
    #                     f"Invalid election type: {e}"
    #                 )
    #             if party := e_data.get(f'{e}PARTY'):
    #                 if party.startswith('REP'):
    #                     info['party'] = PoliticalPartyCodesBase.REPUBLICAN
    #                 elif party.startswith('DEM'):
    #                     info['party'] = PoliticalPartyCodesBase.DEMOCRATIC
    #                 else:
    #                     info['party'] = None
    #             info.setdefault('attributes', {}).update(
    #                 {
    #                     'city': 'Austin',
    #                     'file_election_code': e
    #                 }
    #             )
    #             info['state'] = 'TX'
    #             e_details = ElectionTypeDetails(**info)
    #             info['election_id'] = e_details.id
    #             election_detailed_list.add(e_details)
    #             vote_obj = ElectionVote(**info)
    #             election_list.append(vote_obj)
    #     # self.elections = sorted(election_detailed_list, key=lambda x: x.vote_date)
    #     self.votes = sorted(election_list, key=lambda x: x.vote_date)
    #     # self.collected_elections = election_detailed_list
    #     return self



    # @staticmethod
    # def PENNSYLVANIA(self) -> Type[ValidatorConfig]:

