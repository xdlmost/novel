# -*- coding: utf-8 -*-
import scrapy
from biqu.items import Charpter,NovelInfo
import os,json
from urllib import request
from urllib.parse import urljoin

import sys
sys.path.append("..")
from app.dao.models import NovelContent,NovelInfo



class UpdateSpider(scrapy.Spider):
    name = 'update'
    allowed_domains = ['52bqg.com']
#    start_urls = ['https://www.52bqg.com/book_1/']
    basedir='../data'
    novelIndexList=[]
    seprater='^&*'
    def get_novelIndex(self):
        return os.path.join(self.basedir,'novelIndex')

    def read_novelIndexList(self):
        if os.path.isfile(self.get_novelIndex()):
            with open (self.get_novelIndex() ,'r')as f:
                line=f.readline()
                if line:
                    self.novelIndexList.append(line.split(self.seprater)[0].strip())
                line=f.readline()

    def start_requests(self):
#        self.read_novelIndexList()
        for bookNum in range(1,101):
            book='book_%d'%(bookNum)
            if not book in self.novelIndexList:
                yield self.make_requests_from_url('https://www.52bqg.com/%s/'%(book))

    def append_novel_index(self,novel_id,isVailid):
        with open (self.get_novelIndex() ,'a')as f:
            f.write('%s%s%s\n'%(novel_id,self.seprater,isVailid))

    def get_novel_base_dir(self,novelid):
        return os.path.join(self.basedir,novelid)

    def get_info_file(self,novelid):
        return os.path.join(self.get_novel_base_dir(novelid),'00000-info.json')

    def get_contentList_file(self,novelid):
        return os.path.join(self.get_novel_base_dir(novelid),'00000-contentList')

    def get_contentList(self,novelid,response):
        ret=[]
        url=response.url
        charpterNodeList=response.xpath("//*[@id='list']/dl/node()")
        for i in range(len(charpterNodeList)):
            node=charpterNodeList[i]
            a={}
            if -1!=node.extract().find('dt'):
                a['title']=node.xpath('./text()').extract_first()
                a['url']=''
                a['index']=i
            elif -1!=node.extract().find('dd'):
                a['title']=node.xpath('./a/text()').extract_first()
                a['url']=urljoin(response.url,node.xpath('./a/@href').extract_first())
                a['index']=i
        with open(self.get_contentList_file(novelid),'w',encoding='utf-8') as f:
            for c in charpterlist:
                a={}
                content_url=c.xpath("./@href").extract_first()
                a['file_name']=content_url.split('.')[0]
                a['title']=(c.xpath("./text()").extract_first()).replace('\n','  ')
                f. write('%s%s%s\n'%(a['file_name'],self.seprater,a['title']))
                file_name =os.path.join(self.get_novel_base_dir(novelid),'%s.nov'%(a['file_name']))
                if not os.path.isfile(file_name):
                    ret.append({
                        'url':urljoin(url,content_url),
                        'file_name':file_name,
                        'title':a['title']
                    })
        return ret

        
    def parse(self, response):
        main =response.xpath("//*[@id='maininfo']")
        novelid=response.url[22:-1]
        if len(main)>0:
            if not os.path.isdir(self.get_novel_base_dir(novelid)):
                os.mkdir(self.get_novel_base_dir(novelid))
            if not os.path.isfile(self.get_info_file(novelid)):
                maininfo = main[0]
                info =maininfo.xpath("./*[@id='info']")
                info_to_write={}
                info_to_write['name']=info.xpath("./h1/text()").extract_first()
                info_to_write['author']=info.xpath("./p[contains(text(),'作者')]/a/text()").extract_first() 
                info_to_write['description'] =self.trimDescription(info.xpath("./*[@id='intro']/text()").extract_first())
                info_to_write['url']=response.url

                #cover image
                image_file=os.path.join(self.get_novel_base_dir(novelid),"cover.jpg")
                if not os.path.isfile(image_file):
                    imageUrl=maininfo.xpath("./*[@id='fmimg']/img/@src").extract_first()
                    request.urlretrieve(imageUrl, image_file)

                with open(self.get_info_file(novelid),'w',encoding='utf-8') as f:
                    f.write(json.dumps(info_to_write,ensure_ascii=False))
            
            contentList=self.get_contentList(novelid,response)
            for i in range(len(contentList)):
                pid=''
                nid=''
                if i-1>0:
                    pid=info['list'][i-1]['url']
                if i+1<len(contentList):
                    nid=info['list'][i+1]['url']
                url=contentList[i]['url']
                file_name=contentList[i]['file_name']
                header='%s^&*%s^&*%s^&*%s^&*%s\n'%(info_to_write['author'],info_to_write['name'],contentList[i]['title'],pid,nid)
                yield scrapy.Request(url,callback=self.parse_item(file_name,header))
            self.append_novel_index(novelid,True)
        else:
            self.append_novel_index(novelid,False)

    def trimDescription(self,str):
        pos= str.rfind('\xa0')
        if -1==pos:
            str.strip()
        else:
            return  str[pos:].strip()

    def parse_item(self,filename,header):
        def parse(response):
            content = response.xpath("//*[@id='content']/text()")
            contents=[]
            for ch in content:
                c=ch.root
                pos= c.rfind('\xa0')
                if pos !=-1:
                    contents.append(c[pos:].strip())
            with open(filename,'w',encoding='utf-8') as f:
                f.write(header)
                f.writelines([line+'\n' for line in contents])
        return parse