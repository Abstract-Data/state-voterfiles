from pydantic import BaseModel, validator, Field, root_validator, ValidationError
from uuid import UUID
from typing import Optional, Annotated
from datetime import date, datetime
import app.funcs.validator_funcs as funcs
from app.funcs.record_key_generator import RecordKeyGenerator


class TECRecordValidator(BaseModel):
    recordType: str
    formTypeCd: str
    schedFormTypeCd: Optional[str]
    reportInfoIdent: Optional[int]
    receivedDt: date
    infoOnlyFlag: Optional[bool]
    filerIdent: int
    filerTypeCd: str
    filerTitle: Optional[str]
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
    payeeCompanyName: Optional[str]
    payeeCompanyNameFormatted: Optional[str]
    payeeNameLast: Optional[str]
    payeeNameSuffixCd: Optional[str]
    payeeNameFirst: Optional[str]
    payeeNamePrefixCd: Optional[str]
    payeeNameShort: Optional[str]
    payeeNameFormatted: Optional[str]
    payeeStreetAddr1: Optional[str]
    payeeStreetAddr2: Optional[str]
    payeeStreetCity: Optional[str]
    payeeStreetStateCd: Optional[str]
    payeeStreetCountyCd: Optional[str]
    payeeStreetCountryCd: Optional[str]
    payeeStreetPostalCode: Optional[str]
    payeeStreetPostalCode4: Optional[str]
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
    contributorNameFormatted: Optional[str]
    contributorCompanyName: Optional[str]
    contributorCompanyNameFormatted: Optional[str]
    contributorStreetCity: Optional[str]
    contributorStreetStateCd: Optional[str]
    contributorStreetCountyCd: Optional[str]
    contributorStreetCountryCd: Optional[str]
    contributorStreetPostalCode: Optional[str]
    contributorStreetPostalCode4: Optional[str]
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
    # AbstractContributionHash: Optional[str]
    # AbstractExpenseHash: Optional[str]
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

    # @root_validator(pre=True)
    # @classmethod
    # def filername_parser(cls, values):
    #     filer_name = values.get('filerName', None)
    #
    #     if filer_name:
    #         details = pp.parse(filer_name)
    #         filer_type = details[1]
    #
    #         if 'GivenName' in filer_type:
    #             pfx = re.search(r"(?<=\()(.*?)(?=\))", filer_name)
    #             person_split = HumanName(filer_name)
    #             values['filerTitle'] = person_split.title
    #             values['filerFirstName'] = person_split.first
    #             values['filerLastName'] = person_split.last
    #             values['filerMiddleName'] = funcs.strip_punctuation(
    #                 person_split.middle
    #             ) if person_split.middle else None
    #             values['filerSuffix'] = funcs.strip_punctuation(
    #                 person_split.suffix
    #             ).replace('.', '') if person_split.suffix else None
    #
    #             if person_split.nickname or pfx:
    #                 pfx = pfx.group() if pfx else None
    #                 name_fmt = funcs.strip_nonwhitespace(' '.join(
    #                     [
    #                         pfx,
    #                         person_split.first,
    #                         person_split.middle,
    #                         person_split.last
    #                     ]
    #                 ))
    #             elif person_split.title:
    #                 pfx = person_split.title
    #                 name_fmt = funcs.strip_nonwhitespace(
    #                     ' '.join(
    #                         [
    #                             person_split.title,
    #                             person_split.first,
    #                             person_split.middle,
    #                             person_split.last,
    #                             person_split.suffix
    #                         ]
    #                     )
    #                 )
    #
    #             else:
    #                 pfx = None
    #                 name_fmt = funcs.strip_nonwhitespace(
    #                     ' '.join(
    #                         [
    #                             person_split.first,
    #                             person_split.middle,
    #                             person_split.last,
    #                             person_split.suffix
    #                         ]
    #                     )
    #                 )
    #
    #             values['filerPrefix'] = funcs.strip_nonwhitespace(pfx).replace('.', '') if pfx else None
    #             values['filerNameFormatted'] = funcs.strip_nonwhitespace(name_fmt.upper()) if name_fmt else None
    #
    #         elif 'CorporationName' in [x[1] for x in details]:
    #             companyname = funcs.strip_nonwhitespace(
    #                 ' '.join([x[0] for x in details if x[1] == 'CorporationName'])
    #             )
    #             andcompany = funcs.strip_nonwhitespace(
    #                 ' '.join([x[0] for x in details if x[1] == 'CorporationNameAndCompany'])
    #             )
    #             legaltype = funcs.strip_nonwhitespace(
    #                 ' '.join([x[0] for x in details if x[1] == 'CorporationLegalType'])
    #             )
    #
    #             if all([companyname, andcompany, legaltype]):
    #                 values['filerCompanyName'] = funcs.strip_nonwhitespace(
    #                     ' '.join([companyname, andcompany])
    #                 )
    #                 values['filerCompanyNameFormatted'] = funcs.strip_nonwhitespace(
    #                     ' '.join([companyname, andcompany, legaltype])
    #                 )
    #             elif all([companyname, andcompany]):
    #                 values['filerCompanyName'] = funcs.strip_nonwhitespace(
    #                     ' '.join([companyname, andcompany])
    #                 )
    #                 values['filerCompanyNameFormatted'] = funcs.strip_nonwhitespace(
    #                     ' '.join([companyname, andcompany])
    #                 )
    #             elif all([companyname, legaltype]):
    #                 values['filerCompanyName'] = companyname
    #                 values['filerCompanyNameFormatted'] = funcs.strip_nonwhitespace(
    #                     ' '.join([companyname, legaltype])
    #                 )
    #             elif companyname:
    #                 values['filerCompanyName'] = companyname
    #                 values['filerCompanyNameFormatted'] = companyname
    #
    #             else:
    #                 values['filerCompanyName'] = None
    #                 values['filerCompanyNameFormatted'] = None
    #
    #         else:
    #             values['filerNameFormatted'] = filer_name
    #
    #     return values

    # @root_validator(pre=True)
    # @classmethod
    # def payeename_parser(cls, values):
    #     payee_name = values.get('payeeNameOrganization', None)
    #
    #     if payee_name:
    #         details = pp.parse(payee_name)
    #         payee_type = details[1]
    #
    #         if 'GivenName' in payee_type:
    #             pfx = re.search(r"(?<=\()(.*?)(?=\))", payee_name)
    #             person_split = HumanName(payee_name)
    #             values['filerTitle'] = person_split.title
    #             values['filerFirstName'] = person_split.first
    #             values['filerLastName'] = person_split.last
    #             values['filerMiddleName'] = funcs.strip_punctuation(
    #                 person_split.middle
    #             ) if person_split.middle else None
    #             values['filerSuffix'] = funcs.strip_punctuation(
    #                 person_split.suffix
    #             ).replace('.', '') if person_split.suffix else None
    #
    #             if person_split.nickname or pfx:
    #                 pfx = pfx.group() if pfx else None
    #                 name_fmt = funcs.strip_nonwhitespace(' '.join(
    #                     [
    #                         pfx,
    #                         person_split.first,
    #                         person_split.middle,
    #                         person_split.last
    #                     ]
    #                 ))
    #             elif person_split.title:
    #                 pfx = person_split.title
    #                 name_fmt = funcs.strip_nonwhitespace(
    #                     ' '.join(
    #                         [
    #                             person_split.title,
    #                             person_split.first,
    #                             person_split.middle,
    #                             person_split.last,
    #                             person_split.suffix
    #                         ]
    #                     )
    #                 )
    #
    #             else:
    #                 pfx = None
    #                 name_fmt = funcs.strip_nonwhitespace(
    #                     ' '.join(
    #                         [
    #                             person_split.first,
    #                             person_split.middle,
    #                             person_split.last,
    #                             person_split.suffix
    #                         ]
    #                     )
    #                 )
    #
    #             values['filerPrefix'] = funcs.strip_nonwhitespace(pfx).replace('.', '') if pfx else None
    #             values['filerNameFormatted'] = funcs.strip_nonwhitespace(name_fmt.upper()) if name_fmt else None
    #
    #         elif 'CorporationName' in [x[1] for x in details]:
    #             companyname = funcs.strip_nonwhitespace(
    #                 ' '.join([x[0] for x in details if x[1] == 'CorporationName'])
    #             )
    #             andcompany = funcs.strip_nonwhitespace(
    #                 ' '.join([x[0] for x in details if x[1] == 'CorporationNameAndCompany'])
    #             )
    #             legaltype = funcs.strip_nonwhitespace(
    #                 ' '.join([x[0] for x in details if x[1] == 'CorporationLegalType'])
    #             )
    #
    #             if all([companyname, andcompany, legaltype]):
    #                 values['filerCompanyName'] = funcs.strip_nonwhitespace(
    #                     ' '.join([companyname, andcompany])
    #                 )
    #                 values['filerCompanyNameFormatted'] = funcs.strip_nonwhitespace(
    #                     ' '.join([companyname, andcompany, legaltype])
    #                 )
    #             elif all([companyname, andcompany]):
    #                 values['filerCompanyName'] = funcs.strip_nonwhitespace(
    #                     ' '.join([companyname, andcompany])
    #                 )
    #                 values['filerCompanyNameFormatted'] = funcs.strip_nonwhitespace(
    #                     ' '.join([companyname, andcompany])
    #                 )
    #             elif all([companyname, legaltype]):
    #                 values['filerCompanyName'] = companyname
    #                 values['filerCompanyNameFormatted'] = funcs.strip_nonwhitespace(
    #                     ' '.join([companyname, legaltype])
    #                 )
    #             elif companyname:
    #                 values['filerCompanyName'] = companyname
    #                 values['filerCompanyNameFormatted'] = companyname
    #
    #             else:
    #                 values['filerCompanyName'] = None
    #                 values['filerCompanyNameFormatted'] = None
    #
    #         else:
    #             values['filerNameFormatted'] = filer_name
    #
    #     return values

        # return values

    # @root_validator(pre=True)
    # @classmethod
    # def hash_generator(cls, values):
    #     if values['AbstractRecordCategory'] == 'EXPENSE':
    #         if values.get('payeeNameOrganization', None):
    #             _cols = [
    #                 'filerName',
    #                 'payeeNameOrganization',
    #                 'expendAmount',
    #                 'expendDt'
    #             ]
    #         elif values.get('payeeNameLast', None):
    #             _cols = [
    #                 'filerName',
    #                 'payeeNameFirst',
    #                 'payeeNameLast',
    #                 'expendAmount',
    #                 'expendDt'
    #             ]
    #         else:
    #             raise ValueError('Payee name must be either a company or a person')
    #
    #         _cols.extend(['payeeStreetAddr1', 'payeeStreetCity', 'payeeStreetPostalCode'])
    #         _string = ''.join([str(values[x]) for x in _cols])
    #         _crypt = RecordKeyGenerator(_string)
    #         values['AbstractExpenseHash'] = _crypt.hash
    #
    #     elif values['AbstractRecordCategory'] == 'CONTRIBUTION':
    #         if values['contributorNameFirst']:
    #             _cols = [
    #                 'filerName',
    #                 'contributorNameFirst',
    #                 'contributorNameLast',
    #                 'contributionDt',
    #                 'contributionAmount'
    #             ]
    #         else:
    #             _cols = [
    #                 'filerName',
    #                 'contributorNameOrganization',
    #                 'contributionDt',
    #                 'contributionAmount'
    #             ]
    #         _string = ''.join([str(values[x]) for x in _cols])
    #         _crypt = RecordKeyGenerator(_string)
    #         values['AbstractContributionHash'] = _crypt.hash
    #     else:
    #         raise ValueError('AbstractRecordCategory must be either "expense" or "contribution"')
    #
    #     return values
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
    expenditure_date = validator('expendDt', pre=True, allow_reuse=True)(funcs.format_dates)
    recieved_date = validator('receivedDt', pre=True, allow_reuse=True)(funcs.format_dates)
    repayment_date = validator('repaymentDt', pre=True, allow_reuse=True)(funcs.format_dates)
    contribution_date = validator('contributionDt', pre=True, allow_reuse=True)(funcs.format_dates)
