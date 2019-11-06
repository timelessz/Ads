from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def getsession(host, user, password, db):
    '''
    获取Orm信息
    :return:
    '''
    config = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8&use_unicode=1' % (user, password, host, db)
    engine = create_engine(config, encoding="utf-8", echo=False)
    session = sessionmaker(bind=engine)
    DBSession = session()
    return DBSession
