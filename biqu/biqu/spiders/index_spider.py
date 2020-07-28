# -*- coding: utf-8 -*-
import scrapy
from biqu.items import Charpter,NovelInfo
import os,json
from urllib import request
from urllib.parse import urljoin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import datetime
sys.path.append("..")
from app.dao.models import NovelContent,NovelInfo,ALL_TYPES
from config.db import DB_CONNECTION
from config.local import COVERS_DIR ,DATA_DIR

class BiquSpider(scrapy.Spider):
    name = 'index'
    allowed_domains = ['52bqg.com']
    basedir='../'+DATA_DIR
    imgdir='../'+COVERS_DIR
    Session = sessionmaker(bind=create_engine(DB_CONNECTION))
    thisSession=None
    def start_requests(self):
        start_urls = [
        'https://www.52bqg.com/',
        'https://www.52bqg.com/xuanhuan/',
        'https://www.52bqg.com/xianxia/',
        'https://www.52bqg.com/dushi/',
        'https://www.52bqg.com/yanqing/',
        'https://www.52bqg.com/lishi/',
        'https://www.52bqg.com/wangyou/',
        'https://www.52bqg.com/kehuan/',
        'https://www.52bqg.com/kongbu/',
        'https://www.52bqg.com/quanben/',
        'https://www.52bqg.com/paihangbang/',
        ]
        for u in start_urls:
            r=scrapy.Request(u,callback=self.parse )
            yield r

    def get_db_session(self):
        if self.thisSession is None:
            self.thisSession=self.Session()
        return self.thisSession

    def novelInfos_in_index(self,response):
        links =response.xpath("//a/@href")
        for link in links:
            linkStr=link.root
            newLinkStr=linkStr
            if linkStr.startswith('https://'):
                newLinkStr=linkStr[8:]
            li=newLinkStr.split('/')
            if (len(li)==3):
                if li[1].startswith('book_') and 0==len(li[2]):
                    newNovelInfo= NovelInfo()
                    newNovelInfo.url=linkStr
                    newNovelInfo.id=li[1]
                    newNovelInfo.create_date=datetime.datetime.now()
                    yield newNovelInfo

    def parse(self, response):
        session = self.get_db_session()
        for info in self.novelInfos_in_index(response):
            session.add(info)
            try:
                session.commit()
            except Exception :
                session.rollback()