from flask import Blueprint ,request,render_template , abort
import os
import json
from config.local import URL_BASE,DATA_DIR,INDEX_MAIN_COUNT,INDEX_OTHER_COUNT,UPDATE_COUNT

plugin = Blueprint('other_index', __name__)
DATA_PATH=DATA_DIR
def hot_novel(session,type):
    from app.dao.models import NovelInfo,NovelContent
    novel_list=session.query(NovelInfo).filter(NovelInfo.type==type,NovelInfo.last_update_date!=None).order_by(NovelInfo.hotness.desc()).limit(INDEX_MAIN_COUNT+UPDATE_COUNT).all()

    main_index_info_count=INDEX_MAIN_COUNT if len(novel_list)>INDEX_MAIN_COUNT else len(novel_list)
    other_index_info_count=len(novel_list)-main_index_info_count

    main_infos=[]
    for info in novel_list[:main_index_info_count]:
        description_path=os.path.join(DATA_DIR,info.id,'00000-description')
        description=''
        with open (description_path,'r',encoding="utf-8") as f:
            description=f.read()
        main_infos.append({
            'title':info.title,
            'author':info.author,
            'bookid':info.id,
            'description':description,
            'latest_charpter_id':info.last_chapter_id,
            'latest_charpter_title':info.last_chapter_title
        })

    other_infos=[]
    for info in novel_list[main_index_info_count:]:
        other_infos.append({
            'title':info.title,
            'author':info.author,
            'type':info.type,
            'bookid':info.id
        })
    return main_infos,other_infos

def update_novel(session,type):
    from app.dao.models import NovelInfo,NovelContent
    novelInfos=session.query(NovelInfo).filter(NovelInfo.type==type,NovelInfo.last_update_date!=None).order_by(NovelInfo.last_chapter_date.desc()).limit(UPDATE_COUNT).all()
    ret=[]
    for info in novelInfos:
        ret.append({
            'bookid':info.id,
            'title':info.title,
            'author':info.author,
            'type':info.type,
            'latest_charpter_id':info.last_chapter_id,
        })
    return ret

def _make_other_ret(type):
    from app import db
    session=db.session
    ret={
        'type':type
    }
    ret['top_hot'],ret['other_hot']=hot_novel(session,ret['type'])
    ret['last_update_chapters_novel']=update_novel(session,type)

    return render_template('other_index.html',data=ret,url_base=URL_BASE)

@plugin.route('/xuanhuan', methods=['GET'])
@plugin.route('/xuanhuan/', methods=['GET'])
def xuanhuan():
    return _make_other_ret('玄幻')

@plugin.route('/xianxia', methods=['GET'])
@plugin.route('/xianxia/', methods=['GET'])
def xianxia():
    return _make_other_ret('仙侠')

@plugin.route('/dushi', methods=['GET'])
@plugin.route('/dushi/', methods=['GET'])
def dushi():
    return _make_other_ret('都市')

@plugin.route('/yanqing', methods=['GET'])
@plugin.route('/yanqing/', methods=['GET'])
def yanqing():
    return _make_other_ret('言情')

@plugin.route('/lishi', methods=['GET'])
@plugin.route('/lishi/', methods=['GET'])
def lishi():
    return _make_other_ret('历史')

@plugin.route('/wangyou', methods=['GET'])
@plugin.route('/wangyou/', methods=['GET'])
def wangyou():
    return _make_other_ret('网游')

@plugin.route('/kehuan', methods=['GET'])
@plugin.route('/kehuan/', methods=['GET'])
def kehuan():
    return _make_other_ret('科幻')

@plugin.route('/kongbu', methods=['GET'])
@plugin.route('/kongbu/', methods=['GET'])
def kongbu():
    return _make_other_ret('恐怖')

    