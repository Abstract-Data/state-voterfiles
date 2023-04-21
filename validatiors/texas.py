import hashlib
import uuid
from funcs.record_keygen import RecordKeyGenerator
from pydantic import BaseModel, ValidationError, validator, Field, root_validator, conint
from typing import Optional, Annotated, Dict
from datetime import date, datetime
import zipcodes


class TexasValidator(BaseModel):
    COUNTY: str
    VUID: conint(ge=0, le=9999999999)
    EDR: date
    STATUS: str
    LNAME: str
    FNAME: str
    MNAME: Optional[str]
    SFX: Optional[str]
    DOB: date
    SEX: str = Field(..., regex='[MFU]')
    RHNUM: Optional[str]
    RDESIG: Optional[str]
    RSTNAME: Optional[str]
    RSTTYPE: Optional[str]
    RSTSFX: Optional[str]
    RUNUM: Optional[str]
    RUTYPE: Optional[str]
    RCITY: str
    RSTATE: str = "TX"
    RZIP: conint(ge=0, le=99999)
    RZIP4: Optional[Annotated[int, Field(ge=0, le=9999)]]
    MADR1: Optional[str]
    MADR2: Optional[str]
    MCITY: Optional[str]
    MST: Optional[str]
    MZIP: Optional[Annotated[int, Field(ge=0, le=99999)]]
    MZIP4: Optional[Annotated[int, Field(ge=0, le=9999)]]
    NEWHD: conint(ge=0, le=150)
    NEWSD: conint(ge=0, le=35)
    NEWCD: conint(ge=0, le=39)
    ABSTRACT_HASH: str
    ABSTRACT_UUID: uuid.UUID
    ABSTRACT_UPDATE: datetime = datetime.now()

    class Config:
        orm_mode = True
        validate_assignment = True
        validate_all = True

    @root_validator(pre=True)
    @classmethod
    def clear_blank_strings(cls, values):
        for k, v in values.items():
            if v in ['', '"']:
                values[k] = None
        return values

    @root_validator(pre=True)
    @classmethod
    def update_county_name(cls, values):
        if values['\ufeffCOUNTY']:
            values['COUNTY'] = values['\ufeffCOUNTY']
        return values

    @root_validator(pre=True)
    @classmethod
    def validate_zip(cls, values):
        _registration_zip = values.get('RZIP', None)
        _mailing_zip = values.get('MZIP', None)

        def run_zip_validation(zip_code):
            if zip_code:
                _length = len(str(zip_code))
                if _length == 5 and str(_length).isnumeric():
                    zip5_col, zip4_col = zip_code, None
                elif _length == 9 and str(_length).isnumeric():
                    zip5_col, zip4_col = zip_code[:5], zip_code[5:]
                elif _length == 10 and '-' in zip_code:
                    zip5_col, zip4_col = zip_code.split('-')
                else:
                    raise ValueError(f'Invalid zip code: {zip_code}')
                return zip5_col, zip4_col

        if _registration_zip:
            values['RZIP'], values['RZIP4'] = run_zip_validation(_registration_zip)

        if _mailing_zip:
            values['MZIP'], values['MZIP4'] = run_zip_validation(_mailing_zip)

        return values

    @validator('DOB', 'EDR', pre=True)
    @classmethod
    def validate_dates(cls, v):
        if v:
            try:
                return datetime.strptime(v, '%Y%m%d').date()
            except ValueError or ValidationError:
                raise ValueError(f'Invalid date format: {v}')

    @root_validator(pre=True)
    @classmethod
    def generate_hash_uuid(cls, values):
        _key_fields = values['LNAME'].lower() + values['FNAME'].lower() + str(values['VUID'])
        _record = RecordKeyGenerator(
            record=_key_fields
        )
        values['ABSTRACT_HASH'] = _record.hash
        values['ABSTRACT_UUID'] = _record.uid
        return values
