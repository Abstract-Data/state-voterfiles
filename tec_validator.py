import probablepeople
from pydantic import BaseModel, validator, Field, root_validator, ValidationError
from typing import Optional, Annotated
from datetime import datetime, date
import probablepeople as pp
from nameparser import HumanName


class TECValidator(BaseModel):
    recordType: Optional[str]
    formTypeCd: Optional[str]
    schedFormTypeCd: Optional[str]
    reportInfoIdent: Optional[int]
    receivedDt: Optional[date]
    infoOnlyFlag: Optional[bool]
    filerIdent: Optional[int]
    filerTypeCd: Optional[str]
    filerTitle: Optional[str]
    filerName: Optional[str]
    filerNameFormatted: Optional[str]
    filerFirstName: Optional[str]
    filerLastName: Optional[str]
    filerMiddleName: Optional[str]
    filerPrefix: Optional[str]
    filerSuffix: Optional[str]
    filerCompanyName: Optional[str]
    expendInfoId: Optional[int]
    expendDt: Optional[date]
    expendAmount: Optional[float]
    expendDescr: Optional[str]
    expendCatCd: Optional[str]
    expendCatDescr: Optional[str]
    itemizeFlag: Optional[bool]
    travelFlag: Optional[bool]
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
    payeeStreetPostalCode: Optional[int]
    payeeStreetRegion: Optional[str]
    creditCardIssuer: Optional[str]
    repaymentDt: Optional[date]
    contributionInfoId: Optional[int]
    contributionDt: Optional[date]
    contributionAmount: Optional[float]
    contributionDescr: Optional[str]
    contributionCatCd: Optional[str]
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
    contributorStreetPostalCode: Optional[int]
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

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        anystr_strip_whitespace = True

    @root_validator(pre=True)
    @classmethod
    def clear_blank_strings(cls, values):
        for k, v in values.items():
            if v in ['', '"']:
                values[k] = None
        return values

    @validator('repaymentDt', 'expendDt', 'contributionDt', 'receivedDt', 'repaymentDt', pre=True)
    @classmethod
    def date_validator(cls, v):
        if v:
            return datetime.strptime(v, '%Y-%m-%d').date()

    @validator('contributorStreetPostalCode', 'payeeStreetPostalCode', pre=True)
    @classmethod
    def _postal_code(cls, value):
        if value:
            if isinstance(value, str):
                return int(value.split('-')[0])

    @root_validator(pre=True)
    @classmethod
    def person_or_organization_parser(cls, values):
        filer_name = values.get('filerName', None)
        if filer_name:
            try:
                details, category = pp.tag(filer_name)
            except probablepeople.RepeatedLabelError:
                category = None
                pass

            if category == 'Person':
                person_split = HumanName(filer_name)
                values['filerTitle'] = person_split.title
                values['filerFirstName'] = person_split.first
                values['filerLastName'] = person_split.last
                values['filerMiddleName'] = person_split.middle
                values['filerSuffix'] = person_split.suffix

                if person_split.nickname == 'The Honorable':
                    pfx = person_split.nickname
                    name_fmt = ' '.join(
                        [
                            person_split.nickname,
                            person_split.first,
                            person_split.middle,
                            person_split.last
                        ]
                    )
                elif person_split.title:
                    pfx = person_split.title
                    name_fmt = ' '.join(
                        [
                            person_split.title,
                            person_split.first,
                            person_split.middle,
                            person_split.last,
                            person_split.suffix
                        ]
                    )
                else:
                    pfx = None
                    name_fmt = ' '.join(
                        [
                            person_split.first,
                            person_split.middle,
                            person_split.last,
                            person_split.suffix
                        ]
                    )

                values['filerPrefix'] = pfx
                values['filerNameFormatted'] = name_fmt.strip()

        return values


    @validator('expendDt','receivedDt', 'repaymentDt', pre=True)
    @classmethod
    def format_dates(cls, v):
        if v:
            return datetime.strptime(v, '%Y-%m-%d').date()
