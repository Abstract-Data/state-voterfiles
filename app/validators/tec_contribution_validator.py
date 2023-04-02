from pydantic import BaseModel, validator, Field, root_validator, ValidationError
from uuid import UUID
from typing import Optional, Annotated
from datetime import date, datetime
import app.funcs.validator_funcs as funcs
from app.funcs.record_key_generator import RecordKeyGenerator


class TECContributionValidator(BaseModel):
    recordType: str
    formTypeCd: str
    schedFormTypeCd: Optional[str]
    reportInfoIdent: Optional[int]
    receivedDt: date
    infoOnlyFlag: Optional[bool]
    filerIdent: int
    filerTypeCd: str
    filerName: Optional[str]
    contributionInfoId: Optional[int]
    contributionDt: date
    contributionAmount: Optional[float]
    contributionDescr: Optional[str]
    itemizeFlag: Optional[bool]
    travelFlag: Optional[bool]
    contributorPersentTypeCd: Optional[str]
    contributorNameOrganization: Optional[str]
    contributorNameLast: Optional[str]
    contributorNameSuffixCd: Optional[str]
    contributorNameFirst: Optional[str]
    contributorNamePrefixCd: Optional[str]
    contributorNameShort: Optional[str]
    contributorStreetCity: Optional[str]
    contributorStreetStateCd: Optional[str]
    contributorStreetCountyCd: Optional[str]
    contributorStreetCountryCd: Optional[str]
    contributorStreetPostalCode: Optional[str]
    contributorStreetRegion: Optional[str]
    contributorEmployer: Optional[str]
    contributorOccupation: Optional[str]
    contributorJobTitle: Optional[str]
    contributorPacFein: Optional[str]
    contributorOosPacFlag: Optional[bool]
    contributorLawFirmName: Optional[str]
    contributorSpouseLawFirmName: Optional[str]
    contributorParent1LawFirmName: Optional[str]
    contributorParent2LawFirmName: Optional[str]
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
        _contributor_zip = values.get('contributorStreetPostalCode', None)

        if _payee_zip:
            values['payeeStreetPostalCode'], \
                values['payeeStreetPostalCode4'] = funcs.zip_validator(_payee_zip)
        if _contributor_zip:
            values['contributorStreetPostalCode'], \
                values['contributorStreetPostalCode4'] = funcs.zip_validator(_contributor_zip)
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
    # contributor_name = root_validator(pre=True)(funcs.record_name_parser('contributorName'))
    # filer_name = root_validator(pre=True)(funcs.record_name_parser('filerName'))
    recieved_date = validator('receivedDt', pre=True, allow_reuse=True)(funcs.format_dates)
    contribution_date = validator('contributionDt', pre=True, allow_reuse=True)(funcs.format_dates)
