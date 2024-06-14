from RutenCrawler import RutenCrawler
import pandas as pd
import time
import logger

from sqlalchemy.sql.expression import and_
from database import session, engine
from sqlalchemy import func
from models.RegisterCard import RegisterCard

def main():
    logger.logger.info('Program Start!')
    db = session()
    result = db.query(RegisterCard).all()
    data = {
                'CardNo': [r.CardNo for r in result],
            }
    df = pd.DataFrame(data)
    db.close()
    print(df)

    for idx in df.index:
        logger.logger.info('Card No:' + df['CardNo'][idx] + ' start.')
        RutenCrawler(df['CardNo'][idx])
        time.sleep(5)

    
    logger.logger.info('Program End!')



if __name__ == '__main__':
    main()