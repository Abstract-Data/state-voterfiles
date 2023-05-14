from state_voterfiles.funcs.column_formats import VoterInfo
from pathlib import Path

ohio = VoterInfo(Path(__file__).parent / 'field_references' / 'ohio-fields.toml')
texas = VoterInfo(Path(__file__).parent / 'field_references' / 'texas-fields.toml')
