from itertools import groupby
import pandas as pd 
import minizinc
from ProdCrawler import ProdCrawler
from RutenCrawler import RutenCrawler
from models.DailyBind import DailyBind
from database import session, engine
from sqlalchemy import func
from datetime import datetime
import logger
import OptimizingCase
from collections import defaultdict
import numpy as np


db = session()
List = [{'cardno':'QCCP-JP057','cardnumber':3}, {'cardno':'QCCP-JP060','cardnumber':3}]
num_item = len(List)
cardnoList = [item['cardno'] for item in List]
cardnumberList = [item['cardnumber'] for item in List]
maxitemcount = 0 #所有品項中，單一品項最大庫存量
tmpitemcount = 0 #該品項總庫存量
Avg = 0 #該品項平均價格
ResultSet = [] #資料庫篩選後的資料
FinalResultSet = [] #該集合為商品依個數調整，如:ResultSet '001'有三個在同一筆，在 FinalResultSet '001'有三筆
CostMatrix = [] #價格矩陣
print(datetime.now())
for item in List:
    logger.logger.info(item['cardno'])
    if db.query(DailyBind).filter_by(CardNo=item['cardno'], LogDate = datetime.now().date()).count()<=0:
        print('No exist')
        quit()
    else:
        tmp = db.query(DailyBind).filter_by(CardNo=item['cardno'], LogDate = datetime.now().date())
        logger.logger.info('資料庫初始筆數:' + str(tmp.count()))
        tmpitemcount = db.query(func.sum(DailyBind.Qty)).filter_by(CardNo=item['cardno'], LogDate = datetime.now().date()).scalar()
        logger.logger.info('該品項總數量:' + str(tmpitemcount))
        Avg = db.query(func.avg(DailyBind.Price)).filter_by(CardNo=item['cardno'], LogDate = datetime.now().date()).scalar()
        logger.logger.info('該品項平均價格:' + str(Avg))
        tmpresult = db.query(DailyBind).filter(DailyBind.Price <= Avg, DailyBind.Qty > 0, DailyBind.CardNo == item['cardno'], DailyBind.LogDate == datetime.now().date())
        logger.logger.info('價格在平均以下的筆數:' + str(tmpresult.count()))
        tmpitemcount = db.query(func.sum(DailyBind.Qty)).filter(DailyBind.Price <= Avg, DailyBind.Qty > 0, DailyBind.CardNo == item['cardno'], DailyBind.LogDate == datetime.now().date()).scalar()
        logger.logger.info('該品項價格在平均以下的總數量:' + str(tmpitemcount))
        ResultSet.extend(tmpresult)
        if tmpitemcount > maxitemcount:
            maxitemcount = tmpitemcount

for item in ResultSet:
    for i in range(item.Qty):
        FinalResultSet.append(item) #FinalResultSet 為 ResultSet根據QTY擴展的結果

shop_set = set(item.SellerNick for item in ResultSet)
shop_count = len(shop_set)

# 初始化 CostMatrix 和 QtyMatrix
PriceMatrix = defaultdict(lambda: defaultdict(list))
QtyMatrix = defaultdict(lambda: defaultdict(list))
ProdIdMatrix = defaultdict(lambda: defaultdict(list))

# 對 my_collection 中的資料按照 CardNo 和 SellerNick 進行分组
grouped_data = defaultdict(lambda: defaultdict(list))

for item in ResultSet:
    grouped_data[item.CardNo][item.SellerNick].append(item)
    
# for item_name, item in grouped_data['QCCU-JP001'].items():
#     for i in item:
#         print(item_name.rjust(30) + ',' + i.ProdId + ',' + str(i.Price).rjust(5) + ',' + str(i.Qty).rjust(5))
# quit()
    
#對分組的資料進行處理
for cardno, shop_data in grouped_data.items():
    numtobuy = 0 #該卡號需購買數量
    numtobuy = sum(item['cardnumber'] for item in List if item['cardno'] == cardno)
    for shop in shop_set:
        # 對 items 按照價格進行排序
        #sorted_items = sorted([item for item in shop_data if item.SellerNick == shop], key=lambda x: x.Price)

        if shop in shop_data:
            sorted_items = sorted(shop_data[shop], key=lambda x: x.Price)
        else:
            sorted_items = []


        # 獲取每個價格對應的數量
        # price_qty_map = defaultdict(int)
        # for item in sorted_items:
        #     price_qty_map[item.Price] += item.Qty

        # 构建 CostMatrix 和 QtyMatrix
        tmpQty = 0 #計算已加入矩陣的數量
        for idx in range(3):
            if tmpQty < numtobuy:
                if idx < len(sorted_items):
                    Prodid = sorted_items[idx].ProdId
                    Cost = sorted_items[idx].Price
                    if sorted_items[idx].Qty >= numtobuy - tmpQty:
                        Qty = numtobuy - tmpQty
                    else:
                        Qty = sorted_items[idx].Qty
                    tmpQty += sorted_items[idx].Qty
                else:
                    Prodid = ''
                    Cost = 0
                    Qty = 0
            else:
                Prodid = ''
                Cost = 0
                Qty = 0
            
            ProdIdMatrix[cardno][shop].append(Prodid)
            PriceMatrix[cardno][shop].append(Cost)
            QtyMatrix[cardno][shop].append(Qty)

for i in range(num_item):
    row = []
    tmpSet = [item for item in FinalResultSet if item.CardNo == cardnoList[i]]
    for j in range(int(maxitemcount)):
        if j > len(tmpSet) - 1:
            row.append(999999)
        else:
            row.append(tmpSet[j].Price)
        #row.append(j.Price)
    CostMatrix.append(row)

# for item in CostMatrix:
#     logger.logger.info([str(element).zfill(5) for element in item])

try:

    # model = minizinc.Model()
    # model.add_string(OptimizingCase.OptimizeCase1())
    # # Transform Model into a instance
    # gecode = minizinc.Solver.lookup("gecode")
    # inst = minizinc.Instance(gecode, model)
    # inst["num_item"] = num_item
    # inst["shop_count"] = shop_count
    # inst["cardnumberList"] = cardnumberList
    # inst["costs"] = PriceMatrix
    # inst["costs"] = QtyMatrix

    # Solve the instance
    result=''
    PriceMatrixNP = np.array([[value for value in inner_dict.values()] for inner_dict in PriceMatrix.values()])
    QtyMatrixNP = np.array([[value for value in inner_dict.values()] for inner_dict in QtyMatrix.values()])
    ProdIdMatrixNP = np.array([[value for value in inner_dict.values()] for inner_dict in ProdIdMatrix.values()])
    #case1
    #result = OptimizingCase.OptimizeCase1(num_item, maxitemcount, cardnumberList, CostMatrix)
    #case2
    # result = OptimizingCase.OptimizeCase2(num_item, shop_count, cardnumberList, max(cardnumberList), PriceMatrixNP, QtyMatrixNP)
    #case3
    result = OptimizingCase.OptimizeCase3(num_item, shop_count, cardnumberList, max(cardnumberList), PriceMatrixNP, QtyMatrixNP)
    #print(result)
    
    #Case 2
    if False:
        logger.logger.info('total:' + str(result['total']))
        row_str = ''
        for item in shop_set:
            row_str += '[' + item.rjust(24) + '],'
        logger.logger.info('店家名稱:')
        logger.logger.info(row_str)
        logger.logger.info('購買數量:')
        for row in result['x']:
            row_str = ''
            for col in row:
                column_str = '['
                for item in col:
                    column_str += str(item).rjust(7) + ','
                column_str += '],'
                row_str += column_str
            logger.logger.info(row_str)
            
        logger.logger.info('店家庫存:')
        for row in QtyMatrixNP:
            row_str = ''
            for col in row:
                column_str = '['
                for item in col:
                    column_str += str(item).rjust(7) + ','
                column_str += '],'
                row_str += column_str
            logger.logger.info(row_str)
            
        logger.logger.info('店家價格:')
        for row in PriceMatrixNP:
            row_str = ''
            for col in row:
                column_str = '['
                for item in col:
                    column_str += str(item).rjust(7) + ','
                column_str += '],'
                row_str += column_str
            logger.logger.info(row_str)

        for i in range(len(result['x'])):
            for j in range(len(result['x'][i])):
                for k in range(len(result['x'][i][j])):
                    if result['x'][i][j][k] > 0:
                        logger.logger.info("i:"+ str(i) +", j:"+ str(j) + ", k:" + str(k) + ", 值:" + str(result['x'][i][j][k]))
                        logger.logger.info("商品ID:" + str(ProdIdMatrixNP[i][j][k]))
                        logger.logger.info([str(item) for item in ResultSet if item.ProdId == ProdIdMatrixNP[i][j][k]])

    #Case 3
    logger.logger.info('total:' + str(result.objValue))
    row_str = ''
    for item in shop_set:
        row_str += '[' + item.rjust(24) + '],'
    logger.logger.info('店家名稱:')
    logger.logger.info(row_str)
    logger.logger.info('購買數量:')
    for i in range(num_item):
        row_str = ''
        for j in range(shop_count):
            column_str = '['
            for k in range(3):
                column_str += str(int(result.result[i, j, k].varValue)).rjust(7) + ','
            column_str += '],'
            row_str += column_str
        logger.logger.info(row_str)


    logger.logger.info('店家庫存:')
    for row in QtyMatrixNP:
        row_str = ''
        for col in row:
            column_str = '['
            for item in col:
                column_str += str(item).rjust(7) + ','
            column_str += '],'
            row_str += column_str
        logger.logger.info(row_str)
        
    logger.logger.info('店家價格:')
    for row in PriceMatrixNP:
        row_str = ''
        for col in row:
            column_str = '['
            for item in col:
                column_str += str(item).rjust(7) + ','
            column_str += '],'
            row_str += column_str
        logger.logger.info(row_str)

    for i in range(num_item):
        for j in range(shop_count):
            for k in range(3):
                if int(result.result[i, j, k].varValue) > 0:
                    logger.logger.info("i:"+ str(i) +", j:"+ str(j) + ", k:" + str(k) + ", 購買數量:" + str(int(result.result[i, j, k].varValue)) + ", 購買價格:" + str(PriceMatrixNP[i][j][k]))
                    logger.logger.info("商品ID:" + str(ProdIdMatrixNP[i][j][k]))
                    logger.logger.info([str(item) for item in ResultSet if item.ProdId == ProdIdMatrixNP[i][j][k]])


except Exception as e:
    print(e)

print(datetime.now())




