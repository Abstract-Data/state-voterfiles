from pydantic import BaseModel, ValidationError, validator, Field, root_validator, conint
from typing import Optional, Annotated, Dict
from datetime import date

class SOSDetails:
    county: str
    vuid: conint(ge=0, le=9999999999)
    edr: date
    status: str

class VoterInfo:
    lname: str
    fname: str
    mname: Optional[str]
    sfx: Optional[str]
    dob: date
    sex: str = Field(..., regex='[MFU]')

class RegistrationAddressParts:
    rhnum: Optional[str]
    rdesig: Optional[str]
    rstname: Optional[str]
    rsttype: Optional[str]
    rstsfx: Optional[str]
    runum: Optional[str]
    rutype: Optional[str]
    rcity: str
    rstate: str = "TX"
    rzip: conint(ge=0, le=99999)
    rzip4: Optional[Annotated[int, Field(ge=0, le=9999)]]

class MailingAddressParts:
    madr1: Optional[str]
    madr2: Optional[str]
    mcity: Optional[str]
    mstate: Optional[str]
    mzip: Optional[Annotated[int, Field(ge=0, le=99999)]]
    mzip4: Optional[Annotated[int, Field(ge=0, le=9999)]]
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
    NEWHD: Annotated[conint(ge=0, le=150), Field(alias='NEWHD')]
    NEWSD: Annotated[conint(ge=0, le=35), Field(alias='NEWSD')]
    NEWCD: Annotated[conint(ge=0, le=39), Field(alias='NEWCD')]
    ABSTRACT_HASH: str
    ABSTRACT_UUID: uuid.UUID
    ABSTRACT_UPDATE: datetime = datetime.now()