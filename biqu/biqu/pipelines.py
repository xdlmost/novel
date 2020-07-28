# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from biqu.spiders.index_spider import IndexSpider
import os
import json
from urllib import request

class BiquPipeline:
    outpath='../data'
    def open_spider(self, spider):
        if isinstance(spider,IndexSpider):
            self.fo = open(os.path.join(self.outpath,'novelIndex.csv'), 'w')

    def process_item(self, item, spider):
        if isinstance(spider,IndexSpider):
            data = "{},{},{},{},{}\n".format(item['novelid'],item['name'], item['author'], item['url'],item['isVailid'])
            self.fo.write(data)
            if item['isVailid']:
                dirName=os.path.join(self.outpath,item['novelid'])
                if not os.path.isdir(dirName):
                    os.mkdir(dirName)
                with open(os.path.join(dirName,'index.json') ,'w',encoding='utf-8') as w:
                    aa=json.dumps(item._values)
                    w.write(json.dumps(item._values,ensure_ascii=False))
                request.urlretrieve(item['imageUrl'], os.path.join(dirName,"cover.jpg"))
            return item
        else:
            with open(os.path.join(self.outpath,item['filename']) ,'w',encoding='utf-8') as w:
                w.writelines([line+'\n' for line in item['content']])

    def close_spider(self, spider):
        if isinstance(spider,IndexSpider):
            self.fo.close()
