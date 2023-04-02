from pydantic import BaseModel, validator, Field, root_validator, ValidationError
from uuid import UUID
from typing import Optional, Annotated
from datetime import date, datetime
import app.funcs.validator_funcs as funcs
from app.funcs.record_key_generator import RecordKeyGenerator


class TECExpenseValidator(BaseModel):
    recordType: Optional[str]
    formTypeCd: Optional[str]
    schedFormTypeCd: Optional[str]
    reportInfoIdent: Optional[int]
    receivedDt: date
    infoOnlyFlag: Optional[bool]
    filerIdent: Optional[int]
    filerTypeCd: Optional[str]
    filerName: Optional[str]
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
    expendAmount: Optional[float]
    expendDescr: Optional[str]
    expendCatCd: Optional[str]
    expendCatDescr: Optional[str]
    itemizeFlag: Optional[str]
    travelFlag: Optional[str]
    politicalExpendCd: Optional[bool]
    reimburseIntendedFlag: Optional[bool]
    srcCorpContribFlag: Optional[bool]
    capitalLivingexpFlag: Annotated[Optional[str], Field(max_length=1)]
    payeePersentTypeCd: Optional[str]
    payeeNameOrganization: Optional[str]
    payeeNameLast: Optional[str]
    payeeNameSuffixCd: Optional[str]
    payeeNameFirst: Optional[str]
    payeeNamePrefixCd: Optional[str]
    payeeNameShort: Optional[str]
    payeeStreetAddr1: Optional[str]
    payeeStreetAddr2: Optional[str]
    payeeStreetCity: Optional[str]
    payeeStreetStateCd: Optional[str]
    payeeStreetCountyCd: Optional[str]
    payeeStreetCountryCd: Optional[str]
    payeeStreetPostalCode: Optional[str]
    payeeStreetRegion: Optional[str]
    creditCardIssuer: Optional[str]
    repaymentDt: Optional[date]
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

        values['payeeStreetPostalCode'], values['payeeStreetPostalCode4'] = funcs.zip_validator(_payee_zip)
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
