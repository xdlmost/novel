# coding: utf-8

# sqlacodegen mysql+pymysql://root:@127.0.0.1:3306/novel

# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, String,text
from sqlalchemy.dialects.mysql import INTEGER,TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base    

Base = declarative_base()
metadata = Base.metadata

ALL_TYPES=['玄幻', '仙侠', '都市', '言情', '历史', '网游', '科幻', '恐怖']

class NovelInfo(Base):
    __tablename__ = 'novel_info'

    id = Column(String(100), primary_key=True)
    url = Column(String(100), nullable=False)
    type = Column(INTEGER(11))
    title = Column(String(100))
    author = Column(String(100))
    frequency = Column(INTEGER(11))
    last_update_date = Column(DateTime)
    create_date = Column(DateTime)
    hotness = Column(INTEGER(11))
    last_chapter_id = Column(String(100))
    last_chapter_title = Column(String(100))
    last_chapter_date = Column(DateTime)
    last_chapter_index = Column(INTEGER(11))


class NovelContent(Base):
    __tablename__ = 'novel_content'

    id = Column(String(100), primary_key=True, nullable=False)
    novelid = Column(ForeignKey('novel_info.id'), primary_key=True, nullable=False, index=True)
    index = Column(INTEGER(11), nullable=False)
    url = Column(String(100), nullable=False)
    create_date = Column(DateTime)
    title = Column(String(100))
    isover = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    pid = Column(String(100))
    nid = Column(String(100))