from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Dict
from datetime import date, datetime


class TECContributionGetter(BaseModel):
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
    contributorZipCode5: Optional[int]
    contributorZipCode4: Optional[int]
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
    AbstractRecordErrors: Dict[str, str] = {}
    AbstractRecordUUID: UUID
    AbstractRecordUpdateDt: datetime

    class Config:
        orm_mode = True
