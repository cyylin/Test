from sqlalchemy import Column, String, DateTime, DECIMAL, Integer
from database import Base

class DailyBind(Base):
    __tablename__ = 'DailyBind'

    ProdId = Column(String, primary_key = True)
    ProdName = Column(String(15000))
    CardNo = Column(String)
    Spec = Column(String, primary_key = True)
    SpecSub = Column(String, primary_key = True)
    Price = Column(Integer)
    Currency = Column(String)
    Qty = Column(Integer)
    CardType = Column(Integer)
    SellerNick = Column(String)
    LogDate = Column(DateTime(timezone=False), primary_key=True)

    def __init__(self, ProdId, ProdName, CardNo, Spec, SpecSub, Price, Currency, Qty, CardType, SellerNick, LogDate):
        self.ProdId = ProdId
        self.ProdName = ProdName
        self.CardNo = CardNo
        self.Spec = Spec
        self.SpecSub = SpecSub
        self.Price = Price
        self.Currency = Currency
        self.Qty = Qty
        self.CardType = CardType
        self.SellerNick = SellerNick
        self.LogDate = LogDate

    def __str__(self):
        return f"{self.ProdId},{self.ProdName},{self.CardNo},{self.Spec},{self.SpecSub},{self.Price},{self.Currency},{self.Qty},{self.CardType},{self.SellerNick},{self.LogDate}"    