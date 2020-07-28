
from sqlalchemy import create_engine,func
from sqlalchemy.orm import sessionmaker
from app.dao.models import NovelContent,NovelInfo
import datetime

Session = sessionmaker(bind=create_engine('mysql+pymysql://'))

s=Session()

# info_count=s.query(func.count(NovelInfo.id)).scalar()
# info_update_count=s.query(func.count(NovelInfo.id)).filter(NovelInfo.last_update_date != None).scalar()
# countent_count=s.query(func.count(NovelContent.id)).filter(NovelContent.url!='').scalar()
# countent_download_count=s.query(func.count(NovelContent.id)).filter(NovelContent.url!='',NovelContent.isover==True).scalar()

# with open ('./hehe','a') as f :
#     f. write('%s,%s,%s,%s,%s\n'%(datetime.datetime.now(),info_count,info_update_count,countent_count,countent_download_count))
# print ('info_count:[%s]'%(info_count))
# print ('info_update_count:[%s]'%(info_update_count))
# print ('countent_count:[%s]'%(countent_count))
# print ('countent_download_count:[%s]'%(countent_download_count))

def urls():    
    aa=s.query(NovelInfo.id).all()
    for ni in aa:
        yield 'http://novel.heheking.com/'+ni.id+'/'
    bb=s.query(NovelContent.novelid,NovelContent.id).all()
    for ni in bb:
        yield 'http://novel.heheking.com/'+ni.novelid+'/'+ni.id

index=0
count=3000
index_count=1990
for url in urls():
    if count>=index_count:
        index+=1
        count=0
        with open('post/out_%s.http'%(index),'a') as f:
            f.write('POST http://data.zz.baidu.com/urls?site=novel.heheking.com&token=NE9tkC5H4NjH7pu5 HTTP/1.1\n\n')
    with open('post/out_%s.http'%(index),'a') as f:
        f.write(url+'\n')
    count+=1
