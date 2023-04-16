from pydantic import BaseModel, validator, Field, root_validator, ValidationError
from uuid import UUID
from typing import Optional, Annotated, Dict
from datetime import date, datetime
import app.funcs.validator_funcs as funcs
from app.funcs.record_key_generator import RecordKeyGenerator


class TECExpenseValidator(BaseModel):
    recordType: str
    formTypeCd: str
    schedFormTypeCd: str
    reportInfoIdent: int
    receivedDt: date
    infoOnlyFlag: Optional[str]
    filerIdent: int
    filerTypeCd: Optional[str]
    filerName: str
    filerNameFormatted: Optional[str]
    filerFirstName: Optional[str]
    filerLastName: Optional[str]
    filerMiddleName: Optional[str]
    filerPrefix: Optional[str]
    filerSuffix: Optional[str]
    filerCompanyName: Optional[str]
    filerCompanyNameFormatted: Optional[str]
    expendInfoId: Optional[int]
    expendDt: date
    expendAmount: float
    expendDescr: Optional[str]
    expendCatCd: Optional[str]
    expendCatDescr: Optional[str]
    itemizeFlag: Optional[str]
    travelFlag: Optional[str]
    politicalExpendCd: Optional[str]
    reimburseIntendedFlag: Optional[str]
    srcCorpContribFlag: Optional[str]
    capitalLivingexpFlag: Annotated[Optional[str], Field(max_length=1)]
    payeePersentTypeCd: Optional[str]
    payeeNameOrganization: Optional[str]
    payeeNameLast: Optional[str]
    payeeNameSuffixCd: Optional[str]
    payeeNameFirst: Optional[str]
    payeeNamePrefixCd: Optional[str]
    payeeNameShort: Optional[str]
    payeeStreetAddr1: str
    payeeStreetAddr2: Optional[str]
    payeeStreetCity: str
    payeeStreetStateCd: Optional[str]
    payeeStreetCountyCd: Optional[str]
    payeeStreetCountryCd: Optional[str]
    payeeStreetPostalCode: Optional[str]
    payeeZipCode5: Optional[int]
    payeeZipCode4: Optional[int]
    payeeStreetRegion: Optional[str]
    creditCardIssuer: Optional[str]
    repaymentDt: Optional[date]
    AbstractRecordErrors: Dict[str, str] = {}
    AbstractRecordUUID: UUID
    AbstractRecordUpdateDt: datetime = datetime.now()

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_all = True

    @root_validator(pre=True)
    @classmethod
    def uppercase_values(cls, values):
        for k, v in values.items():
            if isinstance(v, str):
                values[k] = v.upper()
        return values

    @root_validator(pre=True)
    @classmethod
    def clear_blank_strings(cls, values):
        for k, v in values.items():
            if v in ['', '"']:
                values[k] = None
        return values

    @root_validator(pre=True)
    @classmethod
    def _postal_code(cls, values):
        _payee_zip = values.get('payeeStreetPostalCode', None)

        values['payeeZipCode5'], values['payeeZipCode4'], _error = funcs.zip_validator(_payee_zip)
        if _error:
            values['AbstractRecordErrors']['payeeZipCode5'] = _error
        return values
    @root_validator(pre=True)
    @classmethod
    def filer_parser(cls, values):
        result = funcs.record_name_parser(values)
        return result

    @root_validator(pre=True)
    @classmethod
    def abstract_record_hash(cls, values):
        values['AbstractRecordUUID'] = RecordKeyGenerator(''.join(values)).uid
        return values

    expenditure_date = validator('expendDt', pre=True, allow_reuse=True)(funcs.format_dates)
    recieved_date = validator('receivedDt', pre=True, allow_reuse=True)(funcs.format_dates)
    repayment_date = validator('repaymentDt', pre=True, allow_reuse=True)(funcs.format_dates)

