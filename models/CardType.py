from enum import Enum

class CardType(Enum):
    普卡 = 1
    普鑽 = 2
    銀字 = 3
    亮面 = 4
    半鑽 = 5
    金亮 = 6
    全鑽 = 7
    雕鑽 = 8
    斜鑽 = 9
    紅鑽 = 10
    白鑽 = 11
    金鑽 = 12
    彩鑽 = 13
    浮雕 = 14

    其他 = 100

def CheckType(CheckStr):
    cardType = CardType.其他

    for member in reversed(CardType):
        if member.name == "其他":
            continue

        if member.name in CheckStr:
            cardType = member
            break
    
    return cardType.value
