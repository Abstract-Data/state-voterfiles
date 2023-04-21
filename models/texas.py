from conf.postgres import Base
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, JSON
from sqlalchemy.dialects.postgresql import TIMESTAMP, BIGINT


class TexasRecord(Base):
    __tablename__ = "nov2022_texas"
    __table_args__ = {'schema': 'texas'}
    COUNTY = Column(String, nullable=False)
    VUID = Column(BIGINT, primary_key=True)
    EDR = Column(Date, nullable=False)
    STATUS = Column(String, nullable=False)
    LNAME = Column(String, nullable=False)
    FNAME = Column(String, nullable=False)
    MNAME = Column(String, nullable=True)
    SFX = Column(String, nullable=True)
    DOB = Column(Date, nullable=False)
    SEX = Column(String, nullable=False)
    RHNUM = Column(String, nullable=True)
    RDESIG = Column(String, nullable=True)
    RSTNAME = Column(String, nullable=True)
    RSTTYPE = Column(String, nullable=True)
    RSTSFX = Column(String, nullable=True)
    RUNUM = Column(String, nullable=True)
    RUTYPE = Column(String, nullable=True)
    RCITY = Column(String, nullable=False)
    RSTATE = Column(String, nullable=True)
    RZIP = Column(Integer, nullable=False)
    RZIP4 = Column(Integer, nullable=True)
    MADR1 = Column(String, nullable=True)
    MADR2 = Column(String, nullable=True)
    MCITY = Column(String, nullable=True)
    MST = Column(String, nullable=True)
    MZIP = Column(Integer, nullable=True)
    MZIP4 = Column(Integer, nullable=True)
    NEWHD = Column(Integer, nullable=False)
    NEWSD = Column(Integer, nullable=False)
    NEWCD = Column(Integer, nullable=False)
    ABSTRACT_HASH = Column(String, nullable=False)
    ABSTRACT_UUID = Column(String, nullable=False)
    ABSTRACT_UPDATE = Column(DateTime, nullable=False)

