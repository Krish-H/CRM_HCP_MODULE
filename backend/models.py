from sqlalchemy import Column, Integer, String, Text, Date, Boolean
from database import Base

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String)
    product = Column(String)
    samples = Column(String)
    sentiment = Column(String)
    notes = Column(Text)
    follow_up_date = Column(Date, nullable=True)
    escalation = Column(Boolean, default=False)