from dataclasses import dataclass, field
from utils.csv_loader import VoterFileLoader
from validatiors.texas import TexasValidator
from models.texas import TexasRecord
from typing import Callable, List, Generator, Dict
from pydantic import ValidationError
from conf.postgres import SessionLocal, sessionmaker, Base, engine
from tqdm import tqdm


@dataclass
class StateValidator:
    def __init__(self, file, validator, sql_model, **kwargs):
        self.file: VoterFileLoader = file
        self.validator: Callable[[TexasValidator], TexasValidator] = validator
        self.sql_model: Callable[[TexasRecord], TexasValidator] = sql_model
        self.kwargs = kwargs

    def load_file_to_sql(
            self,
            records: List[TexasValidator],
            session: sessionmaker = SessionLocal):

        models = [self.sql_model(**record.dict()) for record in records]
        error_records = []
        records_to_load = []
        _loaded_counter = 0

        with session() as db:
            for record in models:
                records_to_load.append(record)
                if len(records_to_load) == 50000:
                    try:
                        db.add_all(records_to_load)
                        db.commit()
                        _loaded_counter += len(records_to_load)
                    except Exception as e:
                        error_records.extend(records_to_load)
                    records_to_load = []
            db.add_all(records_to_load)
            db.commit()
            _loaded_counter += len(records_to_load)

    def validate(self):
        passed, failed = [], []
        for record in self.file.data:
            try:
                r = self.validator(**record)
                passed.append(r)
            except ValidationError as e:
                failed.append({'error': e,
                               'record': record})

            if self.kwargs.get('load_to_sql', False):
                if len(passed) == 100000:
                    self.load_file_to_sql(passed)
                    passed = []

        if self.kwargs.get('load_to_sql', False):
            self.load_file_to_sql(passed)
            return failed
        else:
            return passed, failed

