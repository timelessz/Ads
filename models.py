# coding: utf-8
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class AdsDomain(Base):
    __tablename__ = 'ads_domain'

    id = Column(INTEGER(11), primary_key=True)
    domain = Column(String(45))
    detail = Column(String(200))
    httpcode = Column(String(45))
    created_at = Column(INTEGER(11))
    updated_at = Column(INTEGER(11))


class AdsSensitive(Base):
    __tablename__ = 'ads_sensitive'

    id = Column(INTEGER(11), primary_key=True)
    domain = Column(String(45), comment='域名')
    href = Column(String(450), comment='链接')
    word = Column(String(45), comment='关键词')
    opstatus = Column(TINYINT(4), comment='操作类型 是不是已经处理了')
    type = Column(String(45), comment='类型  ADS  ATTACK')
    created_at = Column(INTEGER(11))
    updated_at = Column(INTEGER(11))
