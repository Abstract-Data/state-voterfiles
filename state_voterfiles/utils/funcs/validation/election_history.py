from pydantic.dataclasses import dataclass as pydantic_dataclass

from state_voterfiles.utils.validation.texas_elections import TexasElectionHistoryValidator


@pydantic_dataclass
class ElectionValidationFuncs:

    @staticmethod
    def validate_election_history(self):
        if self.data.settings.get('FILE-TYPE') == 'voterfile':
            if _state_name := self.data.settings.get('STATE').get('abbreviation'):
                match _state_name:
                    case 'TX':
                        election_validator = TexasElectionHistoryValidator()
                        if _has_city := self.data.settings.get('CITY'):
                            if _city := _has_city.get('name'):
                                match _city.title():
                                    case 'Austin':
                                        _validator = election_validator.AUSTIN_TEXAS
                            else:
                                raise ValueError(f"City not found in settings: {self.data.settings}")
                        else:
                            _validator = election_validator.TEXAS
                    case _:
                        raise ValueError(f"State not supported: {_state_name}")

                _validator(self)
        return self
