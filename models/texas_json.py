from conf.postgres import Base
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, JSON
from sqlalchemy.dialects.postgresql import TIMESTAMP, BIGINT


class TexasJSON(Base):
    __tablename__ = "nov2022_texas_json"
    __table_args__ = {'schema': 'texas'}
    sec_of_state = Column(JSON)
    voter_details = Column(JSON)
    address = Column(JSON)
    districts = Column(JSON)
    vuid = Column(BIGINT, primary_key=True)
    ABSTRACT_HASH = Column(String, nullable=False)
    ABSTRACT_UUID = Column(String, nullable=False)
