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
    name = 'biqu'
    allowed_domains = ['52bqg.com']
    basedir='../'+DATA_DIR
    imgdir='../'+COVERS_DIR

    Session = sessionmaker(bind=create_engine(DB_CONNECTION))
    info_session=None
    content_session=None
    def start_requests(self):
        content_session = self.get_content_session()
        contents=content_session.query(NovelContent).filter(NovelContent.url!='',NovelContent.isover==False).all()
        for content in contents:
            r= scrapy.Request(content.url,callback=self.parse_novel_content)
            r.meta['novelid']=content.novelid
            r.meta['contentid']=content.id
            r.meta['contentindex']=content.index
            yield r
        session = self.get_info_session()
        index=0
        nis=session.query(NovelInfo).order_by(NovelInfo.last_update_date).all()
        for info in nis:
            if info.last_update_date is None:
                r=scrapy.Request(info.url,callback=self.parse_novel_index )
                r.headers["referer"]='https://www.52bqg.com/'
                r.meta['novelid']=info.id
                index+=1
                yield r
            elif self.need_to_update_content(info):
                r=scrapy.Request(info.url,callback=self.parse_novel_update_list )
                r.headers["referer"]='https://www.52bqg.com/'
                r.meta['novelid']=info.id
                index+=1
                yield r
            if index>=2:
                break

    def need_to_update_content(self,info):
        frequency=info.frequency if info.frequency is not None else 0
        return datetime.datetime.now()-info.last_update_date>datetime.timedelta(hours=frequency)

    def get_info_session(self):
        if self.info_session is None:
            self.info_session=self.Session()
        return self.info_session

    def get_content_session(self):
        if self.content_session is None:
            self.content_session=self.Session()
        return self.content_session

########################### parse_novel_index ########################### 

    def get_novel_base_dir(self,novelid):
        return os.path.join(self.basedir,novelid)

    def get_description_file(self,novelid):
        return os.path.join(self.get_novel_base_dir(novelid),'00000-description')

    def get_content_list_from_response(self,response):
        ret=[]
        charpterNodeList=response.xpath("//*[@id='list']/dl/node()")
        count=len(charpterNodeList)
        for i in range(len(charpterNodeList)):
            node=charpterNodeList[i]
            a={}
            if -1!=node.extract().find('dt'):
                a['title']=node.xpath('./text()').extract_first()
                a['id']='title_%d_'%(i)
                a['url']=''
                a['index']=i
                a['pid']=''
                a['nid']=''
                ret.append(a)
            elif -1!=node.extract().find('dd'):
                if len(node.xpath('./a'))==1:
                    idhtml=node.xpath('./a/@href').extract_first()
                    a['title']=node.xpath('./a/text()').extract_first()
                    a['id']=idhtml.split('.')[0]
                    a['url']=urljoin(response.url,idhtml)
                    a['index']=i
                    pindex=i-1
                    pid=None
                    while pindex>=0 and pid is None:
                        if -1!=charpterNodeList[pindex].extract().find('dd'):
                            if len(charpterNodeList[pindex].xpath('./a'))==1:
                                pid=charpterNodeList[pindex].xpath('./a/@href').extract_first().split('.')[0]
                        pindex-=1
                    a['pid']=pid if pid is not None else ''
                    nindex=i+1
                    nid=None
                    while nindex<count and nid is None:
                        if -1!=charpterNodeList[nindex].extract().find('dd'):
                            if len(charpterNodeList[nindex].xpath('./a'))==1:
                                nid=charpterNodeList[nindex].xpath('./a/@href').extract_first().split('.')[0]
                        nindex+=1
                    a['nid']=nid if nid is not None else ''
                    ret.append(a)
                else:
                    pass
        return ret

    def parse_novel_index(self,response):
        main =response.xpath("//*[@id='maininfo']")
        novelid=response.url[22:-1]
        if len(main)>0:
            if not os.path.isdir(self.get_novel_base_dir(novelid)):
                os.mkdir(self.get_novel_base_dir(novelid))
            maininfo = main[0]
            info =maininfo.xpath("./*[@id='info']")
            info_to_write={}
            info_to_write['name']=info.xpath("./h1/text()").extract_first()
            info_to_write['author']=info.xpath("./p[contains(text(),'作者')]/a/text()").extract_first() 
            info_to_write['description'] =self.trimDescription(info.xpath("./*[@id='intro']/text()").extract())
            titles=response.xpath("//title")
            if len(titles)==1:
                types=titles[0].re('_(.*?)小说_')
                for t in types:
                    if t in ALL_TYPES:
                        info_to_write['type']=t

            with open (self.get_description_file(response.meta['novelid']),'w',encoding='utf-8') as f:
                f.write(info_to_write['description'])

            #cover image
            image_file=os.path.join(self.imgdir,"%s.jpg"%(response.meta['novelid']))
            if not os.path.isfile(image_file):
                imageUrl=maininfo.xpath("./*[@id='fmimg']/img/@src").extract_first()
                request.urlretrieve(imageUrl, image_file)
            infosession=self.get_info_session()
            contentsession=self.get_content_session()
            theNovelInfo=infosession.query(NovelInfo).filter(NovelInfo.id==response.meta['novelid']).one()
            theNovelInfo.title=info_to_write['name']
            theNovelInfo.author=info_to_write['author']
            if 'type' in info_to_write:
                theNovelInfo.type=info_to_write['type']

            chartperListResponse=self.get_content_list_from_response(response)
            lastNovelContent=contentsession.query(NovelContent).filter(NovelContent.novelid==response.meta['novelid']).order_by(NovelContent.index.desc()).first()
            lastNovelContentIndex=lastNovelContent.index if lastNovelContent is not None else -1
            for c in chartperListResponse:
                if c['index']>lastNovelContentIndex:
                    content=NovelContent()
                    content.id=c['id']
                    content.index=c['index']
                    content.title=c['title']
                    content.novelid=response.meta['novelid']
                    content.create_date=datetime.datetime.now()
                    content.url=c['url']
                    content.pid=c['pid']
                    content.nid=c['nid']
                    content.url=c['url']
                    if 0==len(c['url']):
                        content.isover=True
                    contentsession.add(content)
            contentsession.commit()
            theNovelInfo.last_update_date=datetime.datetime.now()
            infosession.commit()
            lastNovelContentToTodate=contentsession.query(NovelContent).filter(NovelContent.novelid==response.meta['novelid'])

            for content in lastNovelContentToTodate:
                if not content.isover and len(content.url)>0:
                    r= scrapy.Request(content.url,callback=self.parse_novel_content)
                    r.meta['novelid']=content.novelid
                    r.meta['contentid']=content.id
                    r.meta['contentindex']=content.index
                    yield r
    
    def parse_novel_update_list(self,response):
        infosession=self.get_info_session()
        contentsession=self.get_content_session()
        chartperListResponse=self.get_content_list_from_response(response)
        lastNovelContent=contentsession.query(NovelContent).filter(NovelContent.novelid==response.meta['novelid']).order_by(NovelContent.index.desc()).first()
        
        lastNovelContentIndex=lastNovelContent.index if lastNovelContent is not None else -1

        for c in chartperListResponse:
            if c['index']>lastNovelContentIndex:
                content=NovelContent()
                content.id=c['id']
                content.index=c['index']
                content.title=c['title']
                content.novelid=response.meta['novelid']
                content.create_date=datetime.datetime.now()
                content.url=c['url']
                content.pid=c['pid']
                content.nid=c['nid']
                contentsession.add(content)
        contentsession.commit()

        infosession.query(NovelInfo).filter(NovelInfo.id==response.meta['novelid']).one().last_update_date=datetime.datetime.now()
        infosession.commit()

        lastNovelContentToTodate=contentsession.query(NovelContent).filter(NovelContent.novelid==response.meta['novelid'])
        for content in lastNovelContentToTodate:
            if not content.isover and len(content.url)>0:
                r= scrapy.Request(content.url,callback=self.parse_novel_content)
                r.meta['novelid']=content.novelid
                r.meta['contentid']=content.id
                r.meta['contentindex']=content.index
                yield r

########################### parse_novel_content ########################### 

    def parse_novel_content(self,response):
        content = response.xpath("//*[@id='content']/text()")
        contents=[]
        for ch in content:
            c=ch.root
            pos= c.rfind('\xa0')
            if pos !=-1:
                contents.append(c[pos:].strip())
        filename =os.path.join(self.get_novel_base_dir(response.meta['novelid']),response.meta['contentid'])
        with open(filename,'w',encoding='utf-8') as f:
            f.writelines([line+'\n' for line in contents])

        session=self.get_content_session()
        thisCharpter=session.query(NovelContent).filter(NovelContent.novelid==response.meta['novelid'],NovelContent.id==response.meta['contentid']).one()
        thisCharpter.isover=True
        
        session.commit()
        infosession=self.get_info_session()
        info=infosession.query(NovelInfo).filter(NovelInfo.id==response.meta['novelid']).one()
        if info.last_chapter_index is None or info.last_chapter_index<response.meta['contentindex']:
            info.last_chapter_index=response.meta['contentindex']
            info.last_chapter_id=thisCharpter.id
            info.last_chapter_title=thisCharpter.title
            info.last_chapter_date=thisCharpter.create_date
            infosession.commit()


    def trimDescription(self,strlist):
        retStr=''
        for str in strlist:
            pos= str.rfind('\xa0')
            if -1==pos:
                retStr+=(str.strip()+'\n')
            else:
                retStr+=(str[pos:].strip()+'\n')
        return retStr

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
