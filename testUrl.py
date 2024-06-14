from itertools import groupby
import pandas as pd 
from ProdCrawler import ProdCrawler
from RutenCrawler import RutenCrawler
from models.DailyBind import DailyBind

List = ProdCrawler('QCCU-JP001', '22409867712378')
#print(DailyBind.ProdName.property.columns[0].type.length)
for item in List:
    print(item)