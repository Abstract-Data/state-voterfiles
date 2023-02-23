from pydantic import BaseModel, Field, root_validator
from typing import Optional, List
from datetime import date, datetime
from app.funcs.record_key_generator import RecordKeyGenerator
import re
import app.funcs.validator_funcs as funcs


class TECFilerInfo(BaseModel):
    recordType: str
    filerIdent: int
    filerTypeCd: str
    filerName: str
    filerNameFormatted: Optional[str]
    filerDeceasedFlag: bool = Field(default=False)
    unexpendContribFilerFlag: Optional[bool]
    modifiedElectCycleFlag: Optional[bool]
    filerJdiCd: Optional[str]
    committeeStatusCd: Optional[str]
    ctaSeekOfficeCd: Optional[str]
    ctaSeekOfficeDistrict: Optional[str]
    ctaSeekOfficePlace: Optional[str]
    ctaSeekOfficeDescr: Optional[str]
    ctaSeekOfficeCountyCd: Optional[str]
    ctaSeekOfficeCountyDescr: Optional[str]
    filerPersentTypeCd: Optional[str]
    filerNameOrganization: Optional[str]
    filerNameLast: Optional[str]
    filerNameSuffixCd: Optional[str]
    filerNameFirst: Optional[str]
    filerNamePrefixCd: Optional[str]
    filerNameShort: Optional[str]
    filerStreetAddr1: Optional[str]
    filerStreetAddr2: Optional[str]
    filerStreetCity: Optional[str]
    filerStreetStateCd: Optional[str]
    filerStreetCountyCd: Optional[str]
    filerStreetCountryCd: Optional[str]
    filerStreetPostalCode: Optional[str]
    filerStreetPostalCode4: Optional[str]
    filerStreetRegion: Optional[str]
    filerMailingAddr1: Optional[str]
    filerMailingAddr2: Optional[str]
    filerMailingCity: Optional[str]
    filerMailingStateCd: Optional[str]
    filerMailingCountyCd: Optional[str]
    filerMailingCountryCd: Optional[str]
    filerMailingPostalCode: Optional[str]
    filerMailingPostalCode4: Optional[str]
    filerMailingRegion: Optional[str]
    filerPrimaryUsaPhoneFlag: Optional[bool]
    filerPrimaryPhoneNumber: Optional[str]
    filerPrimaryPhoneExt: Optional[str]
    filerHoldOfficeCd: Optional[str]
    filerHoldOfficeDistrict: Optional[str]
    filerHoldOfficePlace: Optional[str]
    filerHoldOfficeDescr: Optional[str]
    filerHoldOfficeCountyCd: Optional[str]
    filerHoldOfficeCountyDescr: Optional[str]
    filerFilerpersStatusCd: Optional[str]
    filerEffStartDt: Optional[date]
    filerEffStopDt: Optional[date]
    contestSeekOfficeCd: Optional[str]
    contestSeekOfficeDistrict: Optional[str]
    contestSeekOfficePlace: Optional[str]
    contestSeekOfficeDescr: Optional[str]
    contestSeekOfficeCountyCd: Optional[str]
    contestSeekOfficeCountyDescr: Optional[str]
    treasPersentTypeCd: Optional[str]
    treasNameOrganization: Optional[str]
    treasNameLast: Optional[str]
    treasNameSuffixCd: Optional[str]
    treasNameFirst: Optional[str]
    treasNamePrefixCd: Optional[str]
    treasNameShort: Optional[str]
    treasStreetAddr1: Optional[str]
    treasStreetAddr2: Optional[str]
    treasStreetCity: Optional[str]
    treasStreetStateCd: Optional[str]
    treasStreetCountyCd: Optional[str]
    treasStreetCountryCd: Optional[str]
    treasStreetPostalCode: Optional[str]
    treasStreetPostalCode4: Optional[str]
    treasStreetRegion: Optional[str]
    treasMailingAddr1: Optional[str]
    treasMailingAddr2: Optional[str]
    treasMailingCity: Optional[str]
    treasMailingStateCd: Optional[str]
    treasMailingCountyCd: Optional[str]
    treasMailingCountryCd: Optional[str]
    treasMailingPostalCode: Optional[str]
    treasMailingPostalCode4: Optional[str]
    treasMailingRegion: Optional[str]
    treasPrimaryUsaPhoneFlag: Optional[bool]
    treasPrimaryPhoneNumber: Optional[str]
    treasPrimaryPhoneExt: Optional[str]
    treasAppointorNameLast: Optional[str]
    treasAppointorNameFirst: Optional[str]
    treasFilerpersStatusCd: Optional[str]
    treasEffStartDt: Optional[date]
    treasEffStopDt: Optional[date]
    assttreasPersentTypeCd: Optional[str]
    assttreasNameOrganization: Optional[str]
    assttreasNameLast: Optional[str]
    assttreasNameSuffixCd: Optional[str]
    assttreasNameFirst: Optional[str]
    assttreasNamePrefixCd: Optional[str]
    assttreasNameShort: Optional[str]
    assttreasStreetAddr1: Optional[str]
    assttreasStreetAddr2: Optional[str]
    assttreasStreetCity: Optional[str]
    assttreasStreetStateCd: Optional[str]
    assttreasStreetCountyCd: Optional[str]
    assttreasStreetCountryCd: Optional[str]
    assttreasStreetPostalCode: Optional[str]
    assttreasStreetRegion: Optional[str]
    assttreasPrimaryUsaPhoneFlag: Optional[str]
    assttreasPrimaryPhoneNumber: Optional[str]
    assttreasPrimaryPhoneExt: Optional[str]
    assttreasAppointorNameLast: Optional[str]
    assttreasAppointorNameFirst: Optional[str]
    chairPersentTypeCd: Optional[str]
    chairNameOrganization: Optional[str]
    chairNameLast: Optional[str]
    chairNameSuffixCd: Optional[str]
    chairNameFirst: Optional[str]
    chairNamePrefixCd: Optional[str]
    chairNameShort: Optional[str]
    chairStreetAddr1: Optional[str]
    chairStreetAddr2: Optional[str]
    chairStreetCity: Optional[str]
    chairStreetStateCd: Optional[str]
    chairStreetCountyCd: Optional[str]
    chairStreetCountryCd: Optional[str]
    chairStreetPostalCode: Optional[str]
    chairStreetRegion: Optional[str]
    chairMailingAddr1: Optional[str]
    chairMailingAddr2: Optional[str]
    chairMailingCity: Optional[str]
    chairMailingStateCd: Optional[str]
    chairMailingCountyCd: Optional[str]
    chairMailingCountryCd: Optional[str]
    chairMailingPostalCode: Optional[str]
    chairMailingRegion: Optional[str]
    chairPrimaryUsaPhoneFlag: Optional[str]
    chairPrimaryPhoneNumber: Optional[str]
    chairPrimaryPhoneExt: Optional[int]
    AbstractFilerKey: Optional[str]
    AbstractUpdateDate: datetime = datetime.now()
    SOSErrors: List = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
        validate_all = True

    # @root_validator(pre=True)
    # @classmethod
    # def record_filerid(cls, values):
    #     filer_id = values.get('FilerId', None)
    #
    #     if not values.get('FilerId'):
    #         raise ValueError('FilerId is required')
    #
    #     values['recordsFilerId'] = filer_id
    #
    #     return values

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
    def validate_zipcodes(cls,  values):
        _zip_columns = [x for x in TECFilerInfo.schema()['properties'] if x.endswith('PostalCode')]
        for _zip_column in _zip_columns:
            if values.get(_zip_column):
                values[_zip_column], values[f"{_zip_column}4"] = funcs.zip_validator(values[_zip_column])

        return values

    @root_validator(pre=True)
    @classmethod
    def validate_dates(cls, values):
        _date_columns = [x for x in TECFilerInfo.schema()['properties'] if x.endswith('Dt')]
        for _date_column in _date_columns:
            if values.get(_date_column):
                values[_date_column] = funcs.format_dates(values[_date_column])
        return values

    @root_validator(pre=True)
    @classmethod
    def validate_phone(cls, values):
        _phone_columns = [x for x in TECFilerInfo.schema()['properties'] if x.endswith('PhoneNumber')]
        for _phone_column in _phone_columns:
            if values.get(_phone_column):
                values[_phone_column] = funcs.phone_validator(values[_phone_column])
        return values


    @root_validator(pre=True)
    @classmethod
    def parse_names(cls, values):
        if values.get('filerName'):
            name = funcs.name_parser(values['filerName'])
            if name:
                values['filerNameFormatted'] = name.formatted
                values['filerDeceasedFlag'] = name.deceased
        return values

    @root_validator(pre=True)
    @classmethod
    def format_name(cls, values):
        if not values['filerPersentTypeCd'] == 'INDIVIDUAL':
            if values.get('filerName'):
                _name = values['filerName']
                extra_formats = re.findall(r"(?<=\()(.*?)(?=\))", values['filerName'])
                if extra_formats:
                    for each in extra_formats:
                        _name = _name.replace(f"({each})", "")
                values['filerNameFormatted'] = _name.strip()
        return values

    @root_validator
    @classmethod
    def confirm_dissolved(cls, values):
        if 'DISSOLVED' in values['filerName']:
            if not values['committeeStatusCd'] in ['TERMINATED', 'INACTIVE']:
                error = 'Filer is dissolved but committee status is not terminated'
                values['SOSErrors'].append(error)

        return values


    @root_validator(pre=True)
    @classmethod
    def abstract_record_hash(cls, values):
        values['AbstractFilerKey'] = RecordKeyGenerator(''.join([values['filerIdent'], values['filerTypeCd']])).hash
        return values

