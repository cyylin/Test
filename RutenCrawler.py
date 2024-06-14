import requests
import json
import time
import logger
from datetime import datetime
import pandas as pd

from sqlalchemy.sql.expression import and_
from database import session, engine
from sqlalchemy import func
from models.DailyBind import DailyBind
from ProdCrawler import ProdCrawler
from tool import xstr
from itertools import groupby

def RutenCrawler(CardNo):
    offset=1
    ItemDet = []
    ProdList = []
    #CardName = 'WPP4-JP022'

    #connect_db = pymysql.connect('localhost', port=3306, user='root', passwd='123', charset='utf8', db='RutenCrawler')
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
    try:
        while True:
            #print(offset)
            url="https://rtapi.ruten.com.tw/api/search/v3/index.php/core/prod?q=" + CardNo + "&type=direct&sort=rnk%2Fdc&offset="+str(offset)+"&limit=80"#Your URL
            print(url)

            response=requests.get(url, headers= headers)

            PageObject = json.loads(response.content)

            if(len(PageObject['Rows']) == 0):
                break

            offset+=80
            ItemTmp = []
            for Item_dict in PageObject['Rows']:
                ItemTmp.append(Item_dict['Id'])

            urlProdList="https://rtapi.ruten.com.tw/api/prod/v2/index.php/prod?id="#透過蒐集的ID查詢，後面用逗號串起
            for item in ItemTmp:
                urlProdList += item + ','
                
            urlProdList = urlProdList[:-1]#濾掉字尾逗號
            time.sleep(1)
            response = requests.get(urlProdList, headers= headers)
            ProdObject = json.loads(response.content)

            for Item_dict in ProdObject:
                ItemDet.append(Item_dict)
                ProdList.extend(ProdCrawler(CardNo, Item_dict['ProdId']))
                #time.sleep(1)
                
            time.sleep(3)
    except Exception as e:
        print('卡號:' + CardNo + ' 查詢解析有誤' + '\n' + str(e))
        logger.logger.error('卡號:' + CardNo + ' 查詢解析有誤' + '\n' + str(e))
        return

    # 首先，根据 CardType 对 ProdList 进行排序
    sorted_list = sorted(ProdList, key=lambda x: x.CardType)
    #print(sorted_list)

    # 然后，使用 groupby 进行分组
    grouped = groupby(sorted_list, key=lambda x: x.CardType)

    # 可以创建一个字典，将 CardType 作为键，对应的产品列表作为值
    grouped_dict = {key: list(group) for key, group in grouped}

    db = session()
    try:
        db.begin()
        for card_type, prod_list in grouped_dict.items():
            logger.logger.info(f"{CardNo} CardType: {card_type}")
            data = {
                'ProdNo': [prod.ProdNo for prod in prod_list],
                'ProdName': [prod.ProdName for prod in prod_list],
                'CardType': [prod.CardType for prod in prod_list],
                'Price': [int(prod.Price) for prod in prod_list],
            }
            df = pd.DataFrame(data)
            #print(df)

            Q1 = df['Price'].quantile(0.25)
            Q2 = df['Price'].quantile(0.5)
            Q3 = df['Price'].quantile(0.75)
            IQR = Q3 - Q1#IQR=Q3 - Q1
            if Q2 > 100 * Q1:
                CheckValue = 100 * Q1
            else:
                CheckValue = 100 * Q2
            logger.logger.info(f"Q1: {Q1} Q2: {Q2} CheckValue: {CheckValue}")

            filtered_ProdList = [prod for prod in prod_list if int(prod.Price) < CheckValue]

            for item in filtered_ProdList:
                result = db.query(DailyBind).filter_by(ProdId = item.ProdNo, Spec = xstr(item.Spec), 
                                                    SpecSub = xstr(item.SpecSub), 
                                                    LogDate = datetime.now().date()).first()
                if result == None:
                    db.add(DailyBind(item.ProdNo, item.ProdName, CardNo, xstr(item.Spec), xstr(item.SpecSub), 
                                    item.Price, item.Currency, item.RemainNum, item.CardType, item.SellerNick, datetime.now()))

        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        logger.logger.error(str(e))
    finally:
        db.close()




