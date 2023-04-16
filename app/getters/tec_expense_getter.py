from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Annotated, Dict
from datetime import date, datetime
import pandera as pa
from pandera.engines.pandas_engine import PydanticModel



class TECExpenseGetter(BaseModel):
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
    AbstractRecordErrors: Optional[Dict[str, str]]
    AbstractRecordUUID: UUID
    AbstractRecordUpdateDt: datetime = datetime.now()

    class Config:
        orm_mode = True
        validate_all = True
