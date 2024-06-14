import json
import requests
import logger
import pickle
from datetime import datetime
from bs4 import BeautifulSoup
from models.Prod import Prod
from models.CardType import CheckType

def ProdCrawler(query, ItemNo):
    logger.logger.info('Card No:' +query + ' Prod ID:' + ItemNo + ' start.')
    ProdList = []
    #ProdId = "22338751352078"
    #ProdId2 = "22052386609586"#多種規格
    #ProdId3 = "22121686118693"#單規格多項目
    #ProdId4 = "22239450762002"#多規格多項目
    #ProdId5 = "22139336232815"#多規格with賣完
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
    url="https://www.ruten.com.tw/item/show?" + ItemNo#Your URL
    logger.logger.info('Url:' + "https://www.ruten.com.tw/item/show?" + ItemNo)

    #Memo 運費抓法
    #https://rapi.ruten.com.tw/api/shippingfee/v1/seller/{賣家帳號}/event/discount
    #EX: https://rapi.ruten.com.tw/api/shippingfee/v1/seller/spirits850605/event/discount 帳號=spirits850605
    #Return如下，valid = true 代表有折扣
    '''
    {
        "status": "success",
        "data": {
            "vaild": true,
            "event_name": "\u8d85\u5546$99up\u514d\u904b \u2192 \u7acb\u5373\u9818\u904b\u8cbb\u5238",
            "url": "https:\/\/www.ruten.com.tw\/event\/shipping_discount.php",
            "discount_conditions": {
                "HILIFE": {
                    "discount_id": "SD00105299",
                    "arrival_amount": 99,
                    "charge_fee": 0
                },
                "POST_IBOX": {
                    "discount_id": "SD00103972",
                    "arrival_amount": 199,
                    "charge_fee": 0
                },
                "MAPLE": {
                    "discount_id": "SD00103973",
                    "arrival_amount": 299,
                    "charge_fee": 0
                },
                "TCAT": {
                    "discount_id": "SD00103987",
                    "arrival_amount": 299,
                    "charge_fee": 0
                },
                "SEVEN": {
                    "discount_id": "SD00104838",
                    "arrival_amount": 299,
                    "charge_fee": 30
                }
            }
        }
    }
    {
        "status": "success",
        "data": {
            "vaild": false,
            "event_name": "",
            "url": "",
            "discount_conditions": []
        }
    }
    '''

    try:
        response=requests.get(url, headers= headers)
        soup = BeautifulSoup(response.text, features="html.parser")

        data = ""
        CardType = 100
        for script in soup.findAll('script',{'type':'text/javascript'}):
            if(script.text == ""):
                continue
            if ("RT.context" not in script.text):
                continue

            data = script.text
            break

        json_string = data.split('RT.context = ')[1]

        #先處理編碼問題的情況，一些特殊字元如:"，在json.loads反而會報錯，直接做json.loads編碼也是正常的
        #json_string = json_string.encode('utf-8').decode('unicode-escape')
        StartIndex = json_string.index('"item":{')
        EndIndex = json_string.index(',"seller":')
        tmp_string = json_string[StartIndex + 7 : EndIndex]

        dictData = json.loads(tmp_string)
        
        StartIndex = json_string.index('"seller":{')
        EndIndex = json_string.index(',"event":{')
        tmp_string = json_string[StartIndex + 9 : EndIndex]

        dictSeller = json.loads(tmp_string)
        #print(dictSeller)
        #dictData = pickle.load(str(dictData).encode('utf-8').decode('unicode-escape'))
    except Exception as e:
        print('關鍵字:' + query + ' ID:' + ItemNo + ' 網頁解析錯誤' + '\n' + str(e))
        logger.logger.error('關鍵字:' + query + ' ID:' + ItemNo + ' 網頁解析錯誤' + '\n' + str(e))
        return ProdList

    if(query not in dictData['name'].upper()):
        print(query + '與' + str(dictData['no']) + ',' + dictData['name'] + '比對不符')
        logger.logger.info(query + '與' + str(dictData['no']) + ',' + dictData['name'] + '比對不符')
        return ProdList
    if('搜' in dictData['name'].upper()):
        SearchIdx = dictData['name'].rindex('搜')
        TmpProdName = dictData['name'][:SearchIdx]
    else:
        TmpProdName = dictData['name'].upper()

    try:
        CardType = CheckType(TmpProdName)
        if 'specInfo' in dictData:
            if dictData['specInfo'] == False:
                ProdList.append(Prod(dictData['no'], dictData['name'], None, None, dictData['directPrice'], dictData['currency'], dictData['remainNum'], CardType, dictSeller['nick'], datetime.now()))
            else:
                if dictData['specInfo']['level'] == 1:
                    specdict = dictData['specMap']['spec']
                    for key, value in specdict.items():
                        if CardType == 100:
                            CardType = CheckType(key)
                        else:
                            TmpCardType = CheckType(key)
                            if TmpCardType != 100:
                                CardType = TmpCardType
                        ProdList.append(Prod(dictData['no'], dictData['name'], key, None, dictData['specInfo']['specs'][value[0]]['spec_price'], dictData['currency'], dictData['specInfo']['specs'][value[0]]['spec_num'], CardType, dictSeller['nick'], datetime.now()))
                else:
                    specdict = dictData['specMap']['spec']
                    for key, value in specdict.items():
                        if CardType == 100:
                            CardType = CheckType(key)
                        else:
                            TmpCardType = CheckType(key)
                            if TmpCardType != 100:
                                CardType = TmpCardType
                        specdict2 = dictData['specMap']['spec'][key]
                        for specSub in specdict2:
                            if CardType == 100:
                                CardType = CheckType(dictData['specInfo']['specs'][specSub]['spec_name'])
                            else:
                                TmpCardType = CheckType(dictData['specInfo']['specs'][specSub]['spec_name'])
                                if TmpCardType != 100:
                                    CardType = TmpCardType
                            ProdList.append(Prod(dictData['no'], dictData['name'], key, dictData['specInfo']['specs'][specSub]['spec_name'], dictData['specInfo']['specs'][specSub]['spec_price'], dictData['currency'], dictData['specInfo']['specs'][specSub]['spec_num'], CardType, dictSeller['nick'], datetime.now()))

        else:
            if 'directPrice' not in dictData:
                raise ValueError('directPrice 不存在')
            else:
                ProdList.append(Prod(dictData['no'], dictData['name'], None, None, dictData['directPrice'], dictData['remainNum'], dictData['currency'], CardType, dictSeller['nick'], datetime.now()))
    except ValueError as msg:
        print(dictData['no'] + ':has error!' + '\n' + str(msg))
        logger.logger.error(dictData['no'] + ':has error!' + '\n' + str(msg))
    except Exception as e:
        print(dictData['no'] + ':has error!' + '\n' + str(e))
        logger.logger.error(dictData['no'] + ':has error!' + '\n' + str(e))

    return ProdList