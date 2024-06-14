class Prod():

    def __init__(self, ProdNo, ProdName, Spec, SpecSub, Price, Currency, RemainNum, CardType, SellerNick, LogDate):
        self.ProdNo = ProdNo
        self.ProdName = ProdName
        self.Spec = Spec
        self.SpecSub = SpecSub
        self.Price = Price
        self.Currency = Currency
        self.RemainNum = RemainNum
        self.CardType = CardType
        self.SellerNick = SellerNick
        self.LogDate = LogDate

    def __str__(self):
        return f"{self.ProdNo},{self.ProdName},{self.Spec},{self.SpecSub},{self.Price},{self.Currency},{self.RemainNum},{self.CardType},{self.SellerNick},{self.LogDate}"