from utils.csv_loader import VoterFileLoader
from funcs.column_formats import VoterInfo
from pathlib import Path

ohio = VoterInfo(Path(__file__).parent / 'state_formatting' / 'ohio-voter-format.toml')
texas = VoterInfo(Path(__file__).parent / 'state_formatting' / 'texas-voter-format.toml')
