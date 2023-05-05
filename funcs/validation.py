from dataclasses import dataclass, field
from utils.toml_reader import TomlReader
from validatiors.validator_template import ValidatorTemplate


@dataclass
class VoterRecord:
    field_map: TomlReader

    @property
    def validator(self):
        x = self.field_map.data
        return ValidatorTemplate

