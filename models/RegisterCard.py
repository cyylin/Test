from sqlalchemy import Column, String, DateTime, DECIMAL, Integer
from database import Base

class RegisterCard(Base):
    __tablename__ = 'RegisterCard'

    CardNo = Column(String, primary_key = True)
    CardId = Column(String)

    def __init__(self, CardNo, CardId):
        self.CardNo = CardNo
        self.CardId = CardId