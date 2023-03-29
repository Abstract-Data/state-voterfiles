from utils.csv_loader import VoterFileLoader
from funcs.column_formats import VoterInfo
from pathlib import Path

ohio = VoterInfo(Path(__file__).parent / 'state_fields' / 'ohio-fields.toml')
texas = VoterInfo(Path(__file__).parent / 'state_fields' / 'texas-fields.toml')
