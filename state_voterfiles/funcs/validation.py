from dataclasses import dataclass
from state_voterfiles.utils.toml_reader import TomlReader
from state_voterfiles.validatiors.validator_template import ValidatorTemplate


@dataclass
class VoterRecord:
    field_map: TomlReader

    @property
    def validator(self):
        x = self.field_map.data
        return ValidatorTemplate

