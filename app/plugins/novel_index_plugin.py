from flask import Blueprint ,request,render_template , abort
import os
import json
from config.local import URL_BASE,DATA_DIR


plugin = Blueprint('novel_index', __name__)
DATA_PATH=DATA_DIR


@plugin.route('/<string:novelid>', methods=['GET'])
@plugin.route('/<string:novelid>/', methods=['GET'])
def novel_index(novelid):
    from app import db
    from app.dao.models import NovelInfo,NovelContent
    session=db.session

    thisNovelInfo=session.query(NovelInfo).filter(NovelInfo.id==novelid).first()

    if thisNovelInfo is None:
        abort(404)


    description_path=os.path.join(DATA_DIR,novelid,'00000-description')
    description=''
    if not os.path.isfile(description_path):
        abort(404)
    with open (description_path,'r',encoding="utf-8") as f:
        description=f.read()

    NovelContents=session.query(NovelContent).filter(NovelContent.novelid==novelid,NovelContent.isover==True).order_by(NovelContent.index).all()

    ls=[]
    for c in NovelContents:
        ls.append({
            'url':c.id,
            'title':c.title,
            'isTitle':c.id.startswith('title_')
        })

    novel_info={
        'novelid':novelid,
        'title':thisNovelInfo.title,
        'author':thisNovelInfo.author,
        'type':thisNovelInfo.type,
        'description':description,
        'list':ls,
        'last_date':thisNovelInfo.last_chapter_date,
        'last_id': thisNovelInfo.last_chapter_id,
        'last_title':thisNovelInfo.last_chapter_title
    }
    return render_template('novel_index.html',data=novel_info,url_base=URL_BASE)
