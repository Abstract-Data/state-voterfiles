from utils.toml_reader import TomlReader
from utils.csv_loader import VoterFileLoader
from funcs.column_formats import VoterInfo
from pathlib import Path
from pydantic import create_model, validator, ValidationError, root_validator
from typing import Optional
from datetime import date
from collections import Counter
from pprint import pp
import pandas as pd


def ohio_file():
    ohio_cols = TomlReader(Path.cwd() / 'state_fields' / 'ohio-fields.toml').data
    ohio_vf = VoterFileLoader(Path.cwd() / 'voter_files/202303 - HANCOCK OH VOTER REG.txt')
    return ohio_vf, ohio_cols


tx = VoterFileLoader(Path.home() / 'Desktop/VEP 2021-2022/VEP - November 2022/texasnovember2022.csv')
