from flask import Blueprint ,request,render_template , abort
import os
import json
from config.local import URL_BASE,DATA_DIR,INDEX_MAIN_COUNT,INDEX_OTHER_COUNT,UPDATE_COUNT

plugin = Blueprint('index', __name__)
DATA_PATH=DATA_DIR

def make_index_main_infos(novelInfos):
    ret=[]
    for info in novelInfos:
        description_path=os.path.join(DATA_DIR,info.id,'00000-description')
        description=''
        with open (description_path,'r',encoding="utf-8") as f:
            description=f.read()
        ret.append({
            'title':info.title,
            'author':info.author,
            'bookid':info.id,
            'description':description,
            'latest_charpter_id':info.last_chapter_id,
            'latest_charpter_title':info.last_chapter_title
        })
    return ret

def make_index_other_infos(novelInfos):
    ret=[]
    for info in novelInfos:
        ret.append({
            'title':info.title,
            'author':info.author,
            'type':info.type,
            'bookid':info.id,
        })
    return ret

def make_novel_list(session):
    from app.dao.models import NovelInfo,NovelContent
    ret=[]
    for t in ['玄幻', '仙侠', '都市', '网游', '科幻', '恐怖']:
        info={
            'type':t,
            'top_novel':{},
            'other_novels':[]
        }
        novel_list=session.query(NovelInfo).filter(NovelInfo.type==t,NovelInfo.last_update_date!=None).order_by(NovelInfo.hotness.desc()).limit(13).all()
        if len(novel_list)>0:
            top_novel=novel_list[0]
            info['top_novel']['bookid']=top_novel.id
            info['top_novel']['title']=top_novel.title
            description_path=os.path.join(DATA_DIR,top_novel.id,'00000-description')
            if os.path.isfile(description_path):
                with open (description_path,'r',encoding="utf-8") as f:
                    info['top_novel']['description']=f.read()
            for n in novel_list[1:]:
                info['other_novels'].append({
                    'bookid':n.id,
                    'title':n.title,
                    'author':n.author
                })
        ret.append(info)
    return ret

def make_last_in_novel(session):
    from app.dao.models import NovelInfo,NovelContent
    novelInfos=session.query(NovelInfo).filter(NovelInfo.last_update_date!=None).order_by(NovelInfo.create_date.desc()).limit(UPDATE_COUNT).all()
    ret=[]
    for info in novelInfos:
        ret.append({
            'bookid':info.id,
            'title':info.title,
            'author':info.author,
            'type':info.type
        })
    return ret
def make_last_update_chapters_novel(session):
    from app.dao.models import NovelInfo,NovelContent
    novelInfos=session.query(NovelInfo).filter(NovelInfo.last_update_date!=None).order_by(NovelInfo.last_chapter_date.desc()).limit(UPDATE_COUNT).all()
    ret=[]
    for info in novelInfos:
        ret.append({
            'bookid':info.id,
            'title':info.title,
            'author':info.author,
            'type':info.type,
            'latest_charpter_id':info.last_chapter_id,
            'latest_charpter_title':info.last_chapter_title,
            'latest_charpter_date':info.last_chapter_date,
        })
    return ret
    
@plugin.route('/', methods=['GET'])
def index():
    ret={
        'index_main_infos':[],
        'index_other_infos':[]
    }
    from app import db
    from app.dao.models import NovelInfo,NovelContent
    session=db.session

    novelInfos=session.query(NovelInfo).filter(NovelInfo.last_update_date!=None).order_by(NovelInfo.hotness.desc()).limit(INDEX_MAIN_COUNT+INDEX_OTHER_COUNT).all()
    main_index_info_count=INDEX_MAIN_COUNT if len(novelInfos)>INDEX_MAIN_COUNT else len(novelInfos)
    ret['index_main_infos']=make_index_main_infos(novelInfos[:main_index_info_count])

    other_index_info_count=INDEX_OTHER_COUNT if len(novelInfos)>main_index_info_count+INDEX_OTHER_COUNT else len(novelInfos)-main_index_info_count
    ret['index_other_infos']=make_index_other_infos(novelInfos[main_index_info_count:main_index_info_count+other_index_info_count])

    novel_list=make_novel_list(session)
    ret['make_novels_list1']=novel_list[:3]
    ret['make_novels_list2']=novel_list[3:]
    ret ['last_in_novel']=make_last_in_novel(session)
    ret ['last_update_chapters_novel']=make_last_update_chapters_novel(session)

    return render_template('index.html',data=ret,url_base=URL_BASE)