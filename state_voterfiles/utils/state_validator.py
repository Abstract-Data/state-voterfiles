from dataclasses import dataclass
from state_voterfiles.utils.csv_loader import VoterFileLoader
from state_voterfiles.validatiors.texas import TexasValidator
from state_voterfiles.models.texas import TexasRecord
from typing import Callable, List
from pydantic import ValidationError
from state_voterfiles.conf.postgres import SessionLocal, sessionmaker
from tqdm import tqdm


@dataclass
class StateValidator:
    def __init__(self, file, validator, sql_model, **kwargs):
        self.file: VoterFileLoader = file
        self.validator: Callable[[TexasValidator], TexasValidator] = validator
        self.sql_model: Callable[[TexasRecord], TexasValidator] = sql_model
        self.kwargs = kwargs
        self.passed = []
        self.failed = []

    def load_file_to_sql(
            self,
            records: List[TexasValidator],
            session: sessionmaker = SessionLocal):

        models = (self.sql_model(**record.dict()) for record in tqdm(records, desc='Loading Records to SQL', position=0, unit=' records'))
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
                        db.rollback()
                    records_to_load = []
            db.add_all(records_to_load)
            db.commit()
            _loaded_counter += len(records_to_load)

    def validate(self, **kwargs):
        self.passed, self.failed = [], []
        for record in tqdm(self.file.data, desc='Validating Records', position=0, unit=' records'):
            try:
                r = self.validator(**record)
                self.passed.append(r)
            except ValidationError as e:
                self.failed.append(
                    {
                        'error': e,
                        'record': record
                    }
                )

            if self.kwargs.get('load_to_sql') is True:
                if len(self.passed) == 100000:
                    self.load_file_to_sql(self.passed)
                    self.passed = []

        if self.kwargs.get('load_to_sql') is True or kwargs.get('load_to_sql') is True:
            self.load_file_to_sql(self.passed)
            return self.failed
        else:
            return self.passed, self.failed
