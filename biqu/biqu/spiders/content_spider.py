# -*- coding: utf-8 -*-
import scrapy
from biqu.items import Charpter
import os
import json

class ContentSpider(scrapy.Spider):
    name = 'content'
    allowed_domains = ['52bqg.com']
    start_urls = ['https://www.52bqg.com/book_470/347606.html']
    def start_requests(self):
        basedir='../data'
        with open (os.path.join(basedir,'novelIndex.csv') ,'r')as f:
            line=f.readline()
            while line:
                novelid=line.split(',')[0]
                with open(os.path.join(basedir,novelid,'index.json'),'r',encoding='UTF-8') as book_index_f:
                    json_data=json.loads(book_index_f.read())
                    for i in json_data['charpterlist']:
                        yield self.make_requests_from_url('%s%s'%(json_data['url'],i['url']))
                line=f.readline()

    def parse(self, response):
        content = response.xpath("//*[@id='content']/text()")
        item=Charpter()
        item['content']=[]
        for ch in content:
            c=ch.root
            pos= c.rfind('\xa0')
            if pos !=-1:
                item['content'].append(c[pos:].strip())
        url=response.url
        pos=url.find('book_')
        pos2=url.rfind('.')
        item['filename']=url[pos:pos2]+'.nov'
        yield item 
